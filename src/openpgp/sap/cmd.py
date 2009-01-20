#!/usr/bin/env python
"""Application

Funky optparse-ing
------------------
Noticed that something like::

    sap ..perfectly good stuff.. --lit myfile.txt

..where myfile.txt is expected to show up in an 'args' list and --lit is not
an option, DID NOT put myfile.txt in 'args'. For any other invalid option that
was not a substring of '--lit_filename' would just return a "invalid option"
error. Things worked fine (got a good error) if the '--litxxx' substring was
tucked inside the list of options and not near the end.

OK - it looks like if the expected option value is a string (or matches what's
given), then substrings of long options will match.

Dunno know if I like this or not.

:todo: Packet slicing only seems to work with --armor. Check this out.
:todo: Add something like --detach-signed to take a signed message and
    break it into component msg/sigs.
:todo: Extract literal packet data from signed messages, or any messages at
    all..
:todo: Add 'signer_fprint' option to verification to force verification against
    against a particular key packet.
"""
idioms =  """
Create a direct key signature
`````````````````````````````
sap --armor --sign                                           \\
    --keyfile=SIGNER_PATH                                    \\
    --use-key="PRIMARY,SIGNERID"                             \\
    --passphrase="PASSPHRASE"                                \\
    --sig-type=31                                            \\
    --sig-signerid="SIGNERID"                                \\
    --sig-created=1234567890                                 \\
    --sig-note="name1@space1::value1,, name2@space2::value2" \\
    --target-key="PRIMARY,TARGETID"                          \\
    PATH_TO_TARGET
"""

import os
import sys
import logging
import optparse
import getpass

from openpgp.code import *
from api import sign_str, verify_str, encrypt_str, decrypt_str
from armory import looks_armored, list_armored, apply_armor
from list import list_pkts
from util.tool import slice_pkt_str, cat_pkt_str

sep = os.sep
linesep = os.linesep

# The deal is thus:
# - cmd_*() methods gather what's needed for opts & args
#   cmd_order determines when opts & args are gathered
# - run_*() methods figure out what to do with opts & args
#   run_order determines when things are done with opts & args
# - main() brings it all together
#
# Yeah bebe - how about this.. reserve 'g' for sap --grep, the all purpose
# "search these PGP files for some kind of information" ..this will probably
# require the show/list packets to be XML-ized.
#
# remaining letters: bcgjoqrw
#
class SapCmd:

    def __init__(self):
        sys.warnoptions.append('ignore') # quiet normal warnings
        #self.explain_func_map = {'cmd_sign':sign_str,
        #                         'cmd_verify':verify_str,
        #                         'cmd_encrypt':encrypt_str,
        #                         'cmd_decrypt':decrypt_str}

        # 'commandline option': (cmd_* func doc, underlying api func doc)
        self.explain_cmd_map = {'sign':(cmd_sign.__doc__,
                                        sign_str.__doc__),
                                'verify':(cmd_verify.__doc__,
                                          verify_str.__doc__),
                                'encrypt':(cmd_encrypt.__doc__,
                                           encrypt_str.__doc__),
                                'decrypt':(cmd_decrypt.__doc__,
                                           decrypt_str.__doc__)}
        self.cmd_order = [self.cmd_opts]
        self.run_order = [self.run_prompt, self.run_verbage, self.run_sap]

    def cmd_opts(self):
        # actions
        actions = optparse.OptionGroup(self.cmdopt, "actions")
        actions.add_option("-s", "--sign",
                           action="store_true",
                           help="sign ARGS")
        actions.add_option("-y", "--verify",
                           action="store_true",
                           help="verify signatures in ARGS")
        actions.add_option("-e", "--encrypt",
                           action="store_true",
                           help="encrypt ARGS")
        actions.add_option("-d", "--decrypt",
                           action="store_true",
                           help="decrypt ARGS")
        actions.add_option("-x", "--slice-message",
                           type="string", metavar="STR",
                           help="slice packets from message M using 'M[i:j:k]'")
        actions.add_option("-z", "--cat-packets",
                           action="store_true",
                           help="concatenate all packets found in ARGS files")
        actions.add_option("--hexify",
                           action="store_true",
                           help="hexify ARGS")
        actions.add_option("-l", "--show-packets",
                           action="store_true",
                           help="display packet information")
        actions.add_option("-m", "--show-messages",
                           action="store_true",
                           help="display message synopsis")
        #actions.add_option("--show-sigtypes", action="store_true",
        #    help="display list of signature types (for --sig-type)")
        actions.add_option("--explain",
                           type="string",
                           metavar="STR",
                           help="help for action STR")
        actions.add_option("--explain-func",
                           type="string",
                           metavar="STR",
                           help="help for function supporting action STR")
        self.cmdopt.add_option_group(actions)
        # output options
        output = optparse.OptionGroup(self.cmdopt, "output options")
        output.add_option("-a", "--armor",
                          action="store_true",
                          help="output ASCII-armored text")
        output.add_option("-v", "--verbage",
                          type="int",
                          metavar="LVL",
                          default=1,
                          help="increase the chatter to LVL")
        output.add_option("--decompress",
                          action="store_true",
                          help="automatically decompress compressed output")
        output.add_option("--deliteral",
                          action="store_true",
                          help="automatically stringify literal data output")
        self.cmdopt.add_option_group(output)
        # shared parameters
        params = optparse.OptionGroup(self.cmdopt, "parameters")
        params.add_option("-k", "--keyfile",
                          type="string",
                          metavar="FILE",
                          help="look for key(s) in FILE")
        params.add_option("-f", "--detachedfile",
                          type="string",
                          metavar="FILE",
                          help="verify detached signature on FILE")
        params.add_option("-p", "--prompt",
                          action="store_true",
                          help="prompt for decryption/encryption passphrase")
        params.add_option("--passphrase",
                          type="string",
                          metavar="STR",
                          help="specify decryption/encryption passphrase")
        params.add_option("--lit-filename",
                          type="string",
                          metavar="STR",
                          help="filename for literal data")
        params.add_option("--lit-modified",
                          type="int",
                          metavar="INT",
                          help="modification time for literal data")
        self.cmdopt.add_option_group(params)
        # signature options
        sigparams = optparse.OptionGroup(self.cmdopt, "signature parameters")
        output.add_option("-t", "--detach",
                          action="store_true",
                          help="create a detached signature")
        sigparams.add_option("--use-key",
                             type="string",
                             metavar="STR",
                             help='signing key as "primary ID, key ID"')
        sigparams.add_option("--use-userid",
                             type="string",
                             metavar="STR",
                             help='user ID for signing primary as ", UID"')
        sigparams.add_option("--sig-signerid",
                             type="string",
                             metavar="STR",
                             help="declare signing key ID")
        sigparams.add_option("--sig-created",
                             type="int",
                             metavar="INT",
                             help="signature creation timestamp")
        sigparams.add_option("--sig-type",
                             type="int",
                             metavar="INT",
                             help="set signature type to INT")
        sigparams.add_option("--sig-expires",
                             type="int",
                             metavar="INT",
                             help="signature expires INT seconds past creation")
        sigparams.add_option("--sig-note",
                             type="string",
                             metavar="STR",
                             help='"name::value,, .." list of notations')
        sigparams.add_option("--sig-policyurl",
                             type="string",
                             metavar="STR",
                             help="signature policy URL")
        sigparams.add_option("--sig-keyexpires",
                             type="int",
                             metavar="INT",
                             help="set target key expiration to timestamp INT")
        sigparams.add_option("--sig-revoker",
                             type="string",
                             metavar="STR",
                             help='set key revoker as "class,alg,fingerprint"')
        self.cmdopt.add_option_group(sigparams)
        # key message parameters
        keyparams = optparse.OptionGroup(self.cmdopt, "key message parameters")
        keyparams.add_option("--target-key",
                             type="string",
                             metavar="STR",
                             help='identify key packet "primary ID, key ID"')
        keyparams.add_option("--target-userid",
                             type="string",
                             metavar="STR",
                             help='identify primary key via ", user ID"')
        self.cmdopt.add_option_group(keyparams)

    def main(self):
        u = "%prog [action] [output options] [params [signature params]] ARGS"
        self.cmdopt = optparse.OptionParser(u)
        self.output = ""

        for f in self.cmd_order:
            f()

        (self.opts, self.args) = self.cmdopt.parse_args()

        # do whatever opts and args say to do
        for f in self.run_order:
            f()

        print(self.output) # new convention meaning "I really want it printed"

    def run_prompt(self):
        # use --prompt to fill opts.passphrase
        if getattr(self.opts, 'prompt', False):
            self.opts.passphrase = getpass.getpass("Passphrase: ")

    def run_sap(self):

        if self.opts.explain:
            self.output = self.explain_cmd_map[self.opts.explain][0]
        elif self.opts.explain_func:
            self.output = self.explain_cmd_map[self.opts.explain_func][1]
        elif self.opts.show_packets:
           self.output = cmd_show_pkts(opts=self.opts, args=self.args)
        elif self.opts.show_messages:
           self.output = cmd_show_msgs(opts=self.opts, args=self.args)
        elif self.opts.sign:
           self.output = cmd_sign(opts=self.opts, args=self.args)
        elif self.opts.verify:
           self.output = cmd_verify(opts=self.opts, args=self.args)
        elif self.opts.encrypt:
           self.output = cmd_encrypt(opts=self.opts, args=self.args)
        elif self.opts.decrypt:
           self.output = cmd_decrypt(opts=self.opts, args=self.args)
        elif self.opts.hexify:
           self.output = cmd_hexify(opts=self.opts, args=self.args)
        elif self.opts.slice_message:
           self.output = cmd_slice_message(opts=self.opts, args=self.args)
        elif self.opts.cat_packets:
           self.output = cmd_cat_packets(opts=self.opts, args=self.args)

    def run_verbage(self):
        saplog = logging.getLogger("saplog")
        saplog.addHandler(logging.StreamHandler())

        if 0 == self.opts.verbage:
            saplog.setLevel(logging.CRITICAL)
        elif 1 == self.opts.verbage:
            saplog.setLevel(logging.WARNING)
        elif 2 == self.opts.verbage:
            saplog.setLevel(logging.INFO)
        elif 3 <= self.opts.verbage:
            saplog.setLevel(logging.DEBUG)


def cmd_show_pkts(opts=None, args=None):
    """Show packet information.

    The output is just eye candy, subject to change without notice.

    ARGS: files containing packets to show
    """
    from openpgp.sap.util.tool import show_pkts

    p = []

    for filename in args:
        f = file(filename, 'rb')
        s = f.read()
        f.close()

        p.append(show_pkts(s))

    return linesep.join(p)

def cmd_show_msgs(opts=None, args=None):
    """Show message information.

    The output should be helpful as a quick overview and indexed for slicing.

    ARGS: files containing messages to show
    """
    from openpgp.sap.util.tool import show_msgs

    saplog = logging.getLogger("saplog")

    m  = []

    for filename in args: # arguments should all be filenames
        f = file(filename, 'rb')
        s = f.read()
        f.close()
        m.append("'%s':" % filename)
        m.append(show_msgs(s))

    return linesep.join(m)

def cmd_sign(opts=None, args=None):
    """Sign ARGS.

    Options
    -------
    - '--keyfile': file with (private) signing key
    - '--sig-type': int sigtype
    - '--passphrase': private signing key passphrase
    - '--detach': return a detached signature
    - '--target-key': "primary, target_key" key ID/fprint to sign
    - '--target-userid': "primary, userid" user ID/substring to sign
    - '--use-key': "primary, use_key" signing key ID/fprint
    - '--use-userid': "primary, userid" user ID identifying signing key
    - '--sig-created': signature creation timestamp
    - '--sig-signerid': ID of signing key
    - '--sig-note': "name@space::value,, .." notations
    - '--sig-expires': signature expiration timestamp
    - '--sig-policyurl': policy URL string
    - '--sig-keyexpires': target key expiration timestamp
    - '--sig-revoker': "class, alg, fprint" designating a revocation key
    - '--lit-filename': name of signed literal
    - '--lit-modified': modification time of signed literal
    - '--armor': armor the output

    ARGS: filenames to sign
    """
    sigopts = {}
    key_d = ""

    if args: # set signed target
        default_sigtype = SIG_BINARY
        sigopts['target'] = _cat_files(args)

    else:
        default_sigtype = SIG_STANDALONE # no target to sign

    sigtype = getattr(opts, 'sig_type', default_sigtype)

    if getattr(opts, 'keyfile', None) :
        key_d = _cat_files([opts.keyfile]) # keyfile is required

    sigopts['detach'] = getattr(opts, 'detach', False)

    if getattr(opts, 'passphrase', None):
        sigopts['passphrase'] = opts.passphrase

    if getattr(opts, 'armor', None):
        sigopts['armor'] = True

    if getattr(opts, 'target_key', None): # "str primary, str key"
        sigopts['target_key'] = _format_leader(opts.target_key)

    if getattr(opts, 'target_userid', None): # "str primary, str userid"
        sigopts['target_userid'] = _format_leader(opts.target_userid)

    if getattr(opts, 'use_key', None): # "str primary, str key"
        sigopts['use_key'] = _format_leader(opts.use_key)

    if getattr(opts, 'use_userid', None): # "str primary, str userid"
        sigopts['use_userid'] = (primaryid.strip(), userid.strip())

    if getattr(opts, 'sig_created', None): # timestamp str -> int
        sigopts['sig_created'] = int(opts.sig_created)

    if getattr(opts, 'sig_signerid', None): # key ID or fprint
        sigopts['sig_signerid'] = opts.sig_signerid

    if getattr(opts, 'sig_note', None): # "name@space::value,, .." -> [(n,v),..]
        notes = [n.strip() for n in opts.sig_note.split(',,') if n.strip()] # :(
        notes = [tuple(n.split('::', 1)) for n in notes]
        notes = [(n[0].strip(), n[1].strip()) for n in notes]

        if notes:
            sigopts['sig_note'] = notes

    if getattr(opts, 'sig_expires', None): # timestamp str -> int
        sigopts['sig_expires'] = int(opts.sig_expires)

    if getattr(opts, 'sig_policyurl', None): # URL string
        sigopts['sig_policyurl'] = opts.sig_policyurl

    if getattr(opts, 'sig_keyexpires', None): # timestamp str -> int
        sigopts['sig_keyexpires'] = int(opts.sig_keyexpires)

    if getattr(opts, 'sig_revoker', None): # (int cls, int alg, str fprint)
        cls, alg, fprint = opts.split(',', 2)
        sigopts['sig_revoker'] = (int(cls), int(alg), fprint)

    if getattr(opts, 'lit_filename', None): # literal data filename string
        sigopts['lit_filename'] = opts.lit_filename

    if getattr(opts, 'lit_modified', None): # literal data modification timestamp
        sigopts['lit_modified'] = int(lit_modified)

    return sign_str(sigtype, key_d, **sigopts)

def cmd_verify(opts=None, args=None):
    """Verify ARGS.

    Options
    -------
    - '--keyfile': file with (public) verifying key
    - '--detachedfile': file containing detached signature target
    - '--armor': armor the output

    ARGS: filenames with information to verify (includes detached signatures)
    """
    #~ print "opt", opts
    #~ print "args", args
    verifyopts = {}
    signed = _cat_files(args) # need something to verify
    #~ print "KEYs", opts.keyfile
    keys = _cat_files([opts.keyfile])  # keyfile is required

    if getattr(opts, 'detachedfile', None):
        verifyopts['detached'] = _cat_files([opts.detachedfile])

    if getattr(opts, 'armor', None):
        verifyopts['armor'] = True

    print "signed", signed
    #~ print "keys", keys
    print "veryfyopts", verifyopts
    return verify_str(signed, keys, **verifyopts)

def cmd_encrypt(opts=None, args=None):
    """Encrypt ARGS.

    Options
    -------
    - '--keyfile': file with (public) encryption keys
    - '--passphrase': symmetrical encryption passphrase
    - '--target-key': "primary, keyid,, .." key(s) to encrypt to
    - '--target-userid': "primary, userid,, .." user ID(s) identifying keys
    - '--lit-filename': name of signed literal
    - '--lit-modified': modification time of signed literal
    - '--armor': armor the output

    ARGS: filenames with data to encrypt

    Use either 'passphrase' or 'keyfile' with 'target-key' or 'target-userid'.
    """
    encopts = {}
    clrtxt = _cat_files(args) # need something to encrypt

    if getattr(opts, 'keyfile', None):
        encopts['keys'] = _cat_files([opts.keyfile])

    if getattr(opts, 'passphrase', None):
        encopts['passphrase'] = opts.passphrase

    if getattr(opts, 'armor', None):
        encopts['armor'] = True

    if getattr(opts, 'target_key', None): # "str primary, str key,, .."
        keyids = opts.target_key.split(',,')
        primaryid, keyid = keyids.split(',', 1)
        encopts['target_key'] = (primaryid.strip(), keyid.strip())

    if getattr(opts, 'target_userid', None): # "str primary, str userid,, .."
        userids = [u.strip() for u in opts.target_userid.split(',,') if u.strip()]
        userids = [tuple(u.split(',')) for u in userids]
        userids = [(u[0].strip(), u[1].strip()) for u in userids]

        if userids:
            encopts['target_userid'] = userids

    if getattr(opts, 'lit_filename', None): # literal data filename string
        encopts['lit_filename'] = opts.lit_filename

    if getattr(opts, 'lit_modified', None): # literal data modification timestamp
        encopts['lit_modified'] = int(lit_modified)

    return encrypt_str(clrtxt, **encopts)

def cmd_decrypt(opts=None, args=None):
    """Decrypt ARGS.

    Options
    -------
    - '--keyfile': file with (private) decryption keys
    - '--passphrase': decryption passphrase (for private or symmetric key)
    - '--decompress': automatically decompress compressed output
    - '--deliteral': autmatical string-ify literal output
    - '--armor': armor the output

    If you're decrypting text, you'll probably want to use --decompress and
    --deliteral to output readable text. Otherwise, the output will remain
    encoded.

    Don't use --deliteral with --armor since the result of that combination
    remains undefined.

    ARGS: filenames with data to decrypt
    """
    decopts = {}
    cphtxt = _cat_files(args) # need something to decrypt

    if getattr(opts, 'keyfile', None):
        decopts['keys'] = _cat_files([opts.keyfile])

    if getattr(opts, 'passphrase', None):
        decopts['passphrase'] = opts.passphrase

    if getattr(opts, 'decompress', None):
        decopts['decompress'] = True

    if getattr(opts, 'deliteral', None):
        decopts['deliteral'] = True

    if getattr(opts, 'armor', None):
        decopts['armor'] = True

    return decrypt_str(cphtxt, **decopts)

def cmd_hexify(opts=None, args=None):
    """Python-hexify file strings.

    This function reads files and returns them as a copy-n-pasteable hexified
    string. A file named 'test.txt' with data 'abcdef' with an invisible
    newline at the end would be hexified as::

        \\x61\\x62\\x63\\x64\\x65\\x66\\x0a

    If you're seeing double backslashes, just pretend they're single
    backslashes. Better yet, just use the function.

    ARGS: filenames of strings to hexify
    """
    l = []
    _hexify = lambda s: ''.join(['\\x' + hex(ord(c))[2:].zfill(2) for c in s])

    for filename in args:
        l.append("Filename: %s" % filename)
        s = _cat_files([filename])
        l.append(_hexify(s))
        l.append('')

    return linesep.join(l)

def cmd_slice_message(opts=None, args=None):
    """Slice packets for messages from a file.

    Use slice notations "m[x:y:z]" or "L[x:y:z]" where x, y, and z are integers
    (normal Python slice syntax), m is the index of the target message to slice
    and L means slice from leftover packets.

    ARGS: file to slice packets (or message) from (only the first file is used)
    """
    msg_d = _cat_files([args[0]])
    slice_d = opts.slice_message

    pkts = slice_pkt_str(msg_d, slice_d)

    if getattr(opts, 'armor', False):
        s = apply_armor(pkts)

    else:
        s = ''.join([p.rawstr() for p in pkts])

    return s

def cmd_cat_packets(opts=None, args=None):
    """Concatenate packets found in a list of files.

    Options
    -------
    - '--armor': armor the output

    ARGS: files containing packets to concatenate
    """
    p = []

    for filename in args:
        f = file(filename, 'rb')
        p.append(f.read())
        f.close()

    if getattr(opts, 'armor', None):
        armor = True
    else:
        armor = False

    return cat_pkt_str(p, armor=armor)

def _cat_files(fnames):
    sep = ''
    l = []

    for filename in fnames:
        f = file(filename, 'rb')
        s = f.read()
        f.close()
        l.append(s)

        if looks_armored(s):
            sep = os.linesep

    return sep.join(l)

def _format_leader(leader):
    "Format a (primary, block leader) tuple."
    if ',' in leader:
        primaryid, subtarget = leader.split(',', 1)
        return (primaryid.strip(), subtarget.strip())

    return (None, leader.strip())



#def show_sigtypes():
#    """Show a list of signature types (use with --sig-type).
#    """
#    l = ["Signature types (use with --sig-type):"]
#    l.append("0  (0x00) signature over binary data")
#    l.append("1  (0x01) signature over text data")
#    l.append("2  (0x02) standalone signature")
#    l.append("16 (0x10) generic certification of a user ID")
#    l.append("17 (0x11) persona certification of a user ID ")
#    l.append("18 (0x12) casual certification of a user ID ")
#    l.append("19 (0x13) positive certification of a user ID")
#    l.append("24 (0x18) subkey binding certificatoin")
#    l.append("31 (0x1F) direct signature on a key or subkey")
#    l.append("32 (0x20) key revocation")
#    l.append("40 (0x28) subkey revocation")
#    l.append("48 (0x30) certificate revocation")
#    l.append("64 (0x40) timestamp signature")
#    l.append("80 (0x50) third party signature")
#    return os.linesep.join(l)
#

#def dearmor(asc_d, filename):
#    """Return ASCII-armored data to native OpenPGP format.
#
#    :Parameters:
#        - `asc_d`: string of ASCII-armored data block
#
#    :Returns: `OpenPGP.message.Msg.Msg` subclass instance
#    """
#    import OpenPGP.packet as PKT
#    import OpenPGP.packet.LiteralData as LIT
#    players, report = list_players(asc_d, None)
#    for player in players:
#        if isinstance(player, tuple): # we've got ([detached sigs], signed txt)
#            import OpenPGP.packet.OnePassSignature as ONEPASS
#            sigs = player[0]
#            txt = player[1]
#            litparams = { }
#            literal_msg = LIT.create_LiteralDataBody(litparams)
#            opopts = {'sigtype':sigtype,
#                      'alg_hash':ALG_SHA1, # no MUSTs involved, so for now..
#                      'alg_pubkey':seckeymsg._b_primary.leader.body.alg,
#                      'keyid':keyid,
#                      'nest':1} # fix at 1 for now, since we're not handling parallel sigs
#        else:
#            raise NotImplementedError("dearmor() needs work")
#    return players
#

#def get_cmd_opts(cmdopt):
#    # actions
#    actions = optparse.OptionGroup(cmdopt, "actions")
#    actions.add_option("-s", "--sign", action="store_true", help="sign ARGS")
#    actions.add_option("-y", "--verify", action="store_true",
#        help="verify signatures in ARGS")
#    actions.add_option("-e", "--encrypt", action="store_true",
#        help="encrypt ARGS")
#    actions.add_option("-d", "--decrypt", action="store_true",
#        help="decrypt ARGS")
#    actions.add_option("-x", "--slice-message", type="string", metavar="STRING",
#        help="slice packets from message M using 'M[i:j:k]'")
#    actions.add_option("-z", "--cat-packets", action="store_true",
#        help="concatenate all packets found in ARGS files")
#    actions.add_option("--hexify", action="store_true",
#        help="hexify ARGS")
#    actions.add_option("-l", "--show-packets", action="store_true",
#        help="display packet information in provided files")
#    actions.add_option("-m", "--show-messages", action="store_true",
#        help="display synopsis of messages in provided files")
#    #actions.add_option("--show-sigtypes", action="store_true",
#    #    help="display list of signature types (for --sig-type)")
#    actions.add_option("--explain", type="string", metavar="STRING",
#        help="display information about action STRING")
#    actions.add_option("--explain-func", type="string", metavar="STRING",
#        help="display information about the function supporting action STRING")
#    cmdopt.add_option_group(actions)
#    # output options
#    output = optparse.OptionGroup(cmdopt, "output options")
#    output.add_option("-a", "--armor", action="store_true",
#        help="output ASCII-armored text")
#    output.add_option("-v", "--verbage", type="int", metavar="LVL", default=1,
#        help="increase the chatter to LVL")
#    output.add_option("--decompress", action="store_true",
#        help="automatically decompress the output (if it's compressed)")
#    cmdopt.add_option_group(output)
#    # shared parameters
#    params = optparse.OptionGroup(cmdopt, "parameters")
#    params.add_option("-k", "--keyfile", type="string", metavar="FILE",
#        help="look for key(s) in FILE")
#    params.add_option("-f", "--detachedfile", type="string", metavar="FILE",
#        help="verify detached signature on FILE")
#    params.add_option("-p", "--prompt", action="store_true",
#        help="prompt for decryption/encryption passphrase")
#    params.add_option("--passphrase", type="string", metavar="STRING",
#        help="specify decryption/encryption passphrase")
#    params.add_option("--lit_filename", type="string", metavar="STRING",
#        help="filename for literal data")
#    params.add_option("--lit_modified", type="int", metavar="INT",
#        help="modification time for literal data")
#    cmdopt.add_option_group(params)
#    # signature options
#    sigparams = optparse.OptionGroup(cmdopt, "signature parameters")
#    output.add_option("-t", "--detach", action="store_true",
#        help="create a detached signature")
#    sigparams.add_option("--use-key", type="string", metavar="STRING",
#        help='signing key as "primary id, key id"')
#    sigparams.add_option("--use-userid", type="string", metavar="STRING",
#        help='user id identifying signing primary as ", user id"')
#    sigparams.add_option("--sig-type", type="int", metavar="INT",
#        help="force signature type to INT")
#    sigparams.add_option("--sig-expires", type="int", metavar="INT",
#        help="set signature expiration to timestamp INT (past creation)")
#    sigparams.add_option("--sig-note", type="string", metavar="STRING",
#        help="double-comma separated list of name::value notations")
#    sigparams.add_option("--sig-policyurl", type="string", metavar="STRING",
#        help="set signature policy URL to STRING")
#    sigparams.add_option("--sig-keyexpires", type="int", metavar="INT",
#        help="set target key expiration to timestamp INT")
#    sigparams.add_option("--sig-revoker", type="string", metavar="STRING",
#        help="assign key revoker to STRING 'class,alg,fingerprint'")
#    cmdopt.add_option_group(sigparams)
#    # key message parameters
#    keyparams = optparse.OptionGroup(cmdopt, "key message parameters")
#    keyparams.add_option("--target-key", type="string", metavar="STRING",
#        help='identify a particular key with "primary id, target key id"')
#    keyparams.add_option("--target-userid", type="string", metavar="STRING",
#        help='identify a key via user ID with "primary id, target user ID"')
#    cmdopt.add_option_group(keyparams)
#
#def main():
#    saplog = logging.getLogger("saplog")
#    saplog.addHandler(logging.StreamHandler())
#    sys.warnoptions.append('ignore') # quiet normal warnings
#    output = sap_usage
#
#    u = "%prog [action] [output options] [params [signature params]] ARGS"
#    cmdopt = optparse.OptionParser(u)
#
#    get_cmd_opts(cmdopt)
#
#    (opts, args) = cmdopt.parse_args()
#
#    # use --prompt to fill opts.passphrase
#    if getattr(opts, 'prompt', False):
#        opts.passphrase = getpass.getpass("Passphrase: ")
#
#    if 0 == opts.verbage:
#        saplog.setLevel(logging.CRITICAL)
#    elif 1 == opts.verbage:
#        saplog.setLevel(logging.WARNING)
#    elif 2 == opts.verbage:
#        saplog.setLevel(logging.INFO)
#    elif 3 <= opts.verbage:
#        saplog.setLevel(logging.DEBUG)
#
#    if getattr(opts, 'explain', None):
#        func_name = "cmd_%s" % opts.explain.replace('-', '_')
#        output = eval("%s.__doc__" % func_name)
#    elif getattr(opts, 'explain_func', None):
#        func_name = "cmd_%s" % opts.explain_func.replace('-', '_')
#        #co_varnames = eval("%s.func_code.co_varnames" % func_name)
#        if func_name in explain_func_map:
#            func = explain_func_map[func_name]
#            output = func.__doc__
#        else:
#            output = "No further explanation is necessary."
#    elif opts.show_pkts:
#       output = cmd_show_pkts(opts=opts, args=args)
#    elif opts.show_msgs:
#       output = cmd_show_msgs(opts=opts, args=args)
#    elif opts.sign:
#       output = cmd_sign(opts=opts, args=args)
#    elif opts.verify:
#       output = cmd_verify(opts=opts, args=args)
#    elif opts.encrypt:
#       output = cmd_encrypt(opts=opts, args=args)
#    elif opts.decrypt:
#       output = cmd_decrypt(opts=opts, args=args)
#    elif opts.hexify:
#       output = cmd_hexify(opts=opts, args=args)
#    elif opts.slice_message:
#       output = cmd_slice_message(opts=opts, args=args)
#    elif opts.cat_packets:
#       output = cmd_cat_packets(opts=opts, args=args)
#
#    print output

if '__main__' == __name__:
    cmd = SapCmd()
    cmd.main()
