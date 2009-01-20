"Nifty tools"

import os
import logging # dunno if this is necessary here, leftover from code facelift

from openpgp.code import *

import openpgp.sap.text as TXT

from openpgp.sap.armory import looks_armored, list_armored
from openpgp.sap.list import list_pkts, list_msgs

linesep = os.linesep
saplog = logging.getLogger("saplog")

# TODO Tweaked de-armoring from list_players() can be consolidated.
# TODO Turn expensive(?) info log into conditional "if logging level == info:"
def cat_pkt_str(pkt_str_list, armor=False):
    """Concatenate all the packets found in a list of strings.

    :Parameters:
        - `pkt_str_list`: list of OpenPGP strings (native or ASCII-armored)

    :Keywords:
        - `armor`: set to True to return an armored string

    :Returns: string of packets

    :note: ASCII-armored blocks are OK. Native OpenPGP packets are OK. Just
        make sure that both aren't present in a single element in
        `pkt_str_list`.
    """
    from openpgp.sap.armory import looks_armored, list_armored, apply_armor

    saplog.info("Concatenating packets from %s chunks." % len(pkt_str_list))
    pkts = []

    for pkt_d in pkt_str_list:

        if looks_armored(pkt_d):
            pgp_d = ''.join([a.data for a in list_armored(pkt_d)])

        else:
            pgp_d = pkt_d

        pkts.extend(list_pkts(pgp_d))

    if armor:
        s = apply_armor(pkts)

    else:
        s = ''.join([p.rawstr() for p in pkts])

    return s

def slice_pkt_str(msg_d, slice_d):
    """Return a packet slice from a string of OpenPGP data.

    :Parameters:
        - `msg_d`: string OpenPGP data
        - `slice_d`: string slice notation (see `Slice syntax`_)

    :Returns: list of sliced items (message or packet instances)

    .. _Slice syntax:

    Slice syntax
       
        The slice string looks like ``M[x:y:z]`` where ``M`` is either
        an integer message index or the (capital) letter "L" and
        ``[x:y:z]`` is a normal Python slice. An integer value ``M``
        specifies the index of a message in the list of messages to
        slice packets from. The value "L" is used to take a slice from
        the list of leftover packets.
    
    :note: This uses `eval()`, so tread lightly.
    :note: If you shake it, it will break. Play nice.

    :todo: Add deep msg slicing (ex.signed contains literal - 0[0][1:3]).
    """
    if looks_armored(msg_d):    
        msg_d = ''.join([a.data for a in list_armored(msg_d)])

    l = []
    players = list_msgs(list_pkts(msg_d), leftover=l)

    if 'L' == slice_d[0]:
        items = l
        saplog.info("Slicing leftover packets (%s total)." % len(items))

    else:
        msg_idx = int(slice_d[0])
        items = players[msg_idx].seq()
        saplog.info("Slicing message %s of %s." % (msg_idx, len(players)-1))

    pkt_slice = eval("items%s" % slice_d[1:])

    if isinstance(pkt_slice, list):
        return pkt_slice

    else:
        return [pkt_slice]

def show_msgs(d, m_idx=0):
    """Show a synopsis of the packets in a message.
    
    :Parameters:
        - `d`: variable OpenPGP data - may be a string contaning
          OpenPGP packets, a list of OpenPGP messages, or a single
          OpenPGP message instance
        - `m_idx`: counter used to keep track of indentation - should just
          leave it alone

    :Returns: string of message information found in `d`

    Data `d` can either be an unbroken string of native OpenPGP data
    or normal text with one or more ASCII-armored blocks (but not
    both).
    """
    from openpgp.sap.msg.Msg import Msg

    l = []

    if isinstance(d, str):
        if looks_armored(d):
            armored = list_armored(d)
            d = ''.join([a.data for a in armored]) # we may have many armored instances

        msgs = list_msgs(list_pkts(d), leftover=l)

    elif isinstance(d, list): # assume a list of messages
        msgs = d
        l = None

    elif isinstance(d, MSG.Msg.Msg):
        msgs = [d]
        l = None

    r = [] # report, lines of msg/pkt info
    tab = '  '

    if 0 == m_idx:
        m_tab = ''
    else:
        m_tab = tab

    for m in msgs:
        r.append("%s%s %s" % (m_tab, m_idx, TXT.msg_msg(m.type)))
        i_idx = 0
        i_list = []

        for i in m.seq():
            if isinstance(i, Msg):
                r.append(show_msgs(i.rawstr(), i_idx))
            else: # assume packet
                r.append("%s%s %s" % (m_tab+tab, i_idx, show_simple_packet(i)))
            i_idx += 1

        m_idx += 1

    if l:
        r.append("Leftover (non-message) packets")
        for p in l:
            r.append("  %s" % show_simple_packet(p))
        
    return linesep.join(r)

def show_simple_packet(p):
    p_string = ['%s:' % TXT.pkt_msg(p.tag.type)]

    if p.tag.type in [PKT_PUBLICKEY, PKT_PRIVATEKEY, PKT_PUBLICSUBKEY,
                      PKT_PRIVATESUBKEY]:
        p_string.append(p.body.id)
        p_string.append(TXT.alg_pubkey_msg(p.body.alg))

    elif PKT_USERID == p.tag.type:
        p_string.append(p.body.value)

    elif PKT_SIGNATURE == p.tag.type:
        p_string.append(TXT.sig_msg(p.body.type))
        p_string.append("from %s" % p.body.keyid)

    elif PKT_PUBKEYSESKEY == p.tag.type:
        p_string.append(TXT.alg_pubkey_msg(p.body.alg_pubkey))
        p_string.append(p.body.keyid)

    elif PKT_LITERAL == p.tag.type:
        p_string.append(' '.join([p.body.filename, p.body.format, "%s bytes" % len(p.body.data)]))

    return ' '.join(p_string)

def show_pkts(d):
    """Show OpenPGP packet information.

    :Parameters:
        - `d`: variable OpenPGP data - may be a string containing
          OpenPGP packets (native or armored), a list of OpenPGP packets, or a
          single OpenPGP packet instance

    :Returns: string of packet information found in `d`

    :note: Data `d` can either be an unbroken string of native OpenPGP data
        or normal text with one or more ASCII-armored blocks (but not both).
    """
    if isinstance(d, str):
        if looks_armored(d):
            armored = list_armored(d)
            d = ''.join([a.data for a in armored]) # we may have many armored instances
        pkts = list_pkts(d)

    elif isinstance(d, list):
        pkts = d

    elif isinstance(d, PKT.Packet):
        pkts = [d]

    r = []
    for p in pkts:
        r.append(TXT.pkt_msg(p.tag.type))
        l = p.length.size
        if l == 'UNDEFINED':
            l = "Undefined (found %s octets)" % len(p.body.rawstr())
        r.append(" version: %s type: %s bodylength: %s" % (p.tag.version, p.tag.type, l))
        r.append(report_body(p))
        ### packet byte string
        #import OpenPGP.util.strnum as STN
        #r.append("Packet body byte string:")
        #r.append(STN.str2pyhex(p.rawstr()))
        ###
        ### packet body byte string
        #r.append("Packet body byte string:")
        #r.append(STN.str2pyhex(p.body._d))
        ###
    r.append("Pau.")
    return linesep.join(r)

# TODO Major condensing needed.
def report_body(pkt):
    """Return a list of reports on a packet body.

    :Parameters:
        - `pkt`: instance of a `OpenPGP.packet.Packet` subclass

    :Returns: string reporting something about the packet body
    """
    report = []
    body = pkt.body
    if PKT_PUBKEYSESKEY == pkt.tag.type:
        report.append("  version: %s" % body.version)
        report.append("  key id: %s" % body.keyid)
        report.append("  key algorithm: %s (%s)" % (body.alg_pubkey, TXT.alg_pubkey_msg(body.alg_pubkey)))
        if body.alg_pubkey in [ASYM_RSA_EOS, ASYM_RSA_E]:
            report.append("  RSA 'me mod n' bit count: %s" % body.RSA_me_modn.bit_length)
        elif body.alg_pubkey in [ASYM_ELGAMAL_EOS, ASYM_ELGAMAL_E]:
            report.append("  ElGamal 'gk mod p' bit count: %s" % body.ELGAMAL_gk_modp.bit_length)
            report.append("  ElGamal 'myk mod p' bit count: %s" % body.ELGAMAL_myk_modp.bit_length)
    elif PKT_SIGNATURE == pkt.tag.type:
        report.append("  version: %s type: %s %s" % (body.version, body.type, TXT.sig_msg(body.type)))
        report.append("  signer: %s" % body.keyid)
        report.append("  created: %s" % body.created)
        report.append("  hash: %s (%s)" % (body.alg_hash, TXT.alg_hash_msg(body.alg_hash)))
        report.append("  public key algorithm: %s (%s)" % (body.alg_pubkey, TXT.alg_pubkey_msg(body.alg_pubkey)))
        if 4 == body.version:
            report.append("  unhashed data:")
            for s in body.unhashed_subpkts:
                report.append("   %s (%s/%s): %s" % (TXT.sigsub_msg(s.type), s.type, hex(s.type), s.value))
            report.append("  hashed data:")
            for s in body.hashed_subpkts:
                report.append("   %s (%s/%s): %s" % (TXT.sigsub_msg(s.type), s.type, hex(s.type), s.value))
        if body.alg_pubkey in [ASYM_RSA_EOS, ASYM_RSA_S]:
            report.append("  RSA value bit count: %s" % body.RSA.bit_length)
        elif ASYM_DSA == body.alg_pubkey:
            report.append("  DSA 'r' bit count: %s" % body.DSA_r.bit_length)
            report.append("  DSA 's' bit count: %s" % body.DSA_s.bit_length)
        report.append("  hash fragment: %s" % [hex(ord(x)) for x in body.hash_frag])
    elif PKT_SYMKEYSESKEY == pkt.tag.type:
        report.append("  version: %s" % body.version)
        report.append("  algorithm: %s (%s)" % (body.alg, TXT.alg_symkey_msg(body.alg)))
        if 's2k' in body.__dict__:
            report.append("   S2K type: %s" % body.s2k.type)
            if 'alg_hash' in body.s2k.__dict__:
                report.append("   S2K hash: %s (%s)" % (body.s2k.alg_hash, TXT.alg_hash_msg(body.s2k.alg_hash)))
            if 'salt' in body.s2k.__dict__:
                report.append("   S2K salt: %s" % [hex(ord(x)) for x in body.s2k.salt])
            if 'count_code' in body.s2k.__dict__:
                report.append("   S2K count code: %s" % body.s2k.count_code)
            if 'count' in body.s2k.__dict__:
                report.append("   S2K count: %s" % body.s2k.count)
    elif PKT_ONEPASS == pkt.tag.type:
        report.append("  version: %s" % body.version)
        report.append("  signature type: %s (%s)" % (body.type, TXT.sig_msg(body.type)))
        report.append("  key id: %s" % body.keyid)
        report.append("  hash: %s (%s)" % (body.alg_hash, TXT.alg_hash_msg(body.alg_hash)))
        report.append("  key algorithm: %s (%s)" % (body.alg_pubkey, TXT.alg_pubkey_msg(body.alg_pubkey)))
        report.append("  nested: %s" % body.nest)
    elif pkt.tag.type in [PKT_PUBLICKEY, PKT_PUBLICSUBKEY, PKT_PRIVATEKEY, PKT_PRIVATESUBKEY]:
        report.append("  version: %s created: %s" % (body.version, body.created))
        report.append("  algorithm: %s (%s)" % (body.alg, TXT.alg_pubkey_msg(body.alg)))
        report.append("  fingerprint: %s ID: %s" % (body.fingerprint, body.id))
        if body.alg in [ASYM_RSA_EOS, ASYM_RSA_S]:
            report.append("  RSA 'n' bit count: %s" % body.RSA_n.bit_length)
            report.append("  RSA 'n' value: %s" % body.RSA_n.value)
            report.append("  RSA 'e' bit count: %s" % body.RSA_e.bit_length)
            report.append("  RSA 'e' value: %s" % body.RSA_e.value)
        elif ASYM_DSA == body.alg:
            report.append("  DSA 'p' bit count: %s" % body.DSA_p.bit_length)
            report.append("  DSA 'p' value: %s" % body.DSA_p.value)
            report.append("  DSA 'q' bit count: %s" % body.DSA_q.bit_length)
            report.append("  DSA 'q' value: %s" % body.DSA_q.value)
            report.append("  DSA 'g' bit count: %s" % body.DSA_g.bit_length)
            report.append("  DSA 'g' value: %s" % body.DSA_g.value)
            report.append("  DSA 'y' bit count: %s" % body.DSA_y.bit_length)
            report.append("  DSA 'y' value: %s" % body.DSA_y.value)
        elif body.alg in [ASYM_ELGAMAL_EOS, ASYM_ELGAMAL_E]:
            report.append("  ElGamal 'p' bit count: %s" % body.ELGAMAL_p.bit_length)
            report.append("  ElGamal 'p' value: %s" % body.ELGAMAL_p.value)
            report.append("  ElGamal 'g' bit count: %s" % body.ELGAMAL_g.bit_length)
            report.append("  ElGamal 'g' value: %s" % body.ELGAMAL_g.value)
            report.append("  ElGamal 'y' bit count: %s" % body.ELGAMAL_y.bit_length)
            report.append("  ElGamal 'y' value: %s" % body.ELGAMAL_y.value)
        if hasattr(body, 'expires'):
            report.append("  expires: %s" % body.expires)
        if hasattr(body, 'expires'):
            report.append("  expires: %s" % body.expires)
        if pkt.tag.type in [PKT_PRIVATEKEY, PKT_PRIVATESUBKEY]:
            if hasattr(body, 'alg_sym'):
                report.append("  encrypted with algorithm: %s %s" % (body.alg_sym, TXT.alg_symkey_msg(body.alg_sym)))
            if hasattr(body, 's2k_usg'):
                report.append("  S2K usage: %s" % body.s2k_usg)
            if hasattr(body, 'iv'):
                report.append("  IV: %s" % [hex(ord(x)) for x in body.iv])
            if hasattr(body, 's2k'):
                report.append("   S2K type: %s" % body.s2k.type)
                if hasattr(body.s2k, 'alg_hash'):
                    report.append("   S2K hash: %s (%s)" % (body.s2k.alg_hash, TXT.alg_hash_msg(body.s2k.alg_hash)))
                if hasattr(body.s2k, 'salt'):
                    report.append("   S2K salt: %s" % ''.join(['\\x%s' % hex(ord(c))[2:].zfill(2) for c in body.s2k.salt]))
                if hasattr(body.s2k, 'count_code'):
                    report.append("   S2K count code: %s" % body.s2k.count_code)
                if hasattr(body.s2k, 'count'):
                    report.append("   S2K count: %s" % body.s2k.count)
            if hasattr(body, '_enc_d'):
                report.append("  encrypted data: %s octets" % len(body._enc_d))
                #report.append("  encrypted data: %s" % [hex(ord(x)) for x in body._enc_d])
                report.append("  encrypted data: %s" % ''.join(['\\x%s' % hex(ord(c))[2:].zfill(2) for c in body._enc_d]))
            else:
                if body.alg in [ASYM_RSA_EOS, ASYM_RSA_S]:
                    report.append("  Secret RSA 'd' bit count: %s" % body.RSA_d.bit_length)
                    report.append("  Secret RSA 'd' value: %s" % body.RSA_d.value)

                    report.append("  Secret RSA 'p' bit count: %s" % body.RSA_p.bit_length)
                    report.append("  Secret RSA 'p' value: %s" % body.RSA_p.value)

                    report.append("  Secret RSA 'q' bit count: %s" % body.RSA_q.bit_length)
                    report.append("  Secret RSA 'q' value: %s" % body.RSA_q.value)

                    report.append("  Secret RSA 'u' bit count: %s" % body.RSA_u.bit_length)
                    report.append("  Secret RSA 'u' value: %s" % body.RSA_u.value)

                elif ASYM_DSA == body.alg:
                    report.append("  Secret DSA 'x' bit count: %s" % body.DSA_x.bit_length)
                    report.append("  Secret DSA 'x' value: %s" % body.DSA_x.value)
                elif body.alg in [ASYM_ELGAMAL_EOS, ASYM_ELGAMAL_E]:
                    report.append("  Secret ElGamal 'x' bit count: %s" % body.ELGAMAL_x.bit_length)
                    report.append("  Secret ElGamal 'x' value: %s" % body.ELGAMAL_x.value)
            if hasattr(body, 'chksum') and body.chksum: # for chksum == None??
                report.append("  checksum: %s" % [hex(ord(x)) for x in body.chksum])
    elif PKT_COMPRESSED == pkt.tag.type:
        report.append("  compression type %s (%s)" % (pkt.body.alg, TXT.alg_comp_msg(pkt.body.alg)))
    elif PKT_SYMENCDATA == pkt.tag.type:
        report.append("  encrypted data: %s octets" % len(body.data))
    elif PKT_MARKER == pkt.tag.type:
        report.append("  left a mark: %s" % pkt.body.value)
    elif PKT_LITERAL == pkt.tag.type:
        report.append("  format: %s" % pkt.body.format)
        report.append("  modified: %s" % pkt.body.modified)
        report.append("  filename: %s" % pkt.body.filename)
        report.append("  data length: %s" % len(pkt.body.data))
    elif PKT_TRUST == pkt.tag.type:
        pass
    elif PKT_USERID == pkt.tag.type:
        report.append("  ID: %s" % body.value)
    elif PKT_USERATTR == pkt.tag.type:
        pass
    elif PKT_SYMENCINTDATA == pkt.tag.type:
        report.append("  version: %s" % body.version) # suspect exception
        report.append("  encrypted data: %s octets" % len(body.data)) # suspect exception
    elif PKT_MODDETECT == pkt.tag.type: # will this ever be shown?
        report.append("  detection hash: %s" % [hex(ord(x)) for x in body.hash]) # suspect exception
    else:
        pass
    return linesep.join(report)

