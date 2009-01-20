"Key messages"

from openpgp.code import *
from openpgp.sap.exceptions import *
from Msg import Msg

class PGPKeyMsgError(PGPError): pass
class PGPBlockError(PGPError): pass
class PGPBlockSubkeyBindingError(PGPBlockError): pass
class PGPBlockLeaderError(PGPBlockError): pass

class KeyMsg(Msg):
    pass

class PublicKeyMsg(KeyMsg):
    """Transferable Public Key Message

    :IVariables:
        - `primary_id`: string primary key ID
        - `primary_fprint`: string primary key fingerprint
        - `_b_primary`: Block instance primary key block
        - `_b_userids`: dictionary of user ID blocks, keyed by user ID
        - `_b_userattrs`: list of blocks
        - `_b_subkeys`: dictionary of subkey blocks, keyed by subkey ID
 
    :CVariables:
        - `type`: constant MSG_PUBLICKEY (see OpenPGP.constant.messages)
    """
    type = MSG_PUBLICKEY
    def __init__(self, pkts=None, *args, **kwords):
        """Initialize public key message.

        :Parameters:
            - `pkts`: *optional* list of packets to build message with

        :Exceptions:
            - `PGPKeyMsgError`: first block is not a primary key block
        """
        import openpgp.sap.util.ordict as ORD

        self._b_primary = None
        self._b_subkeys = ORD.ordict()
        self._b_userids = ORD.ordict()
        self._b_userattrs = []
       
        if isinstance(pkts, list):

            if pkts[0].tag.type in [PKT_PUBLICKEY, PKT_PRIVATEKEY]:

                # first block must be a public key or secret key
                block = Block(pkts[0].body.id, pkts, idx=0)
                self.new_primary(block) # no signatures are required for primary
                idx = len(block.seq())

                try:
                    while pkts[idx].tag.type not in [PKT_PUBLICKEY,
                                                     PKT_PRIVATEKEY]:
                        # indiscriminate order
                        block = Block(self.primary_id, pkts, idx=idx)

                        if not block.local_bindings:
                            break # subblocks require a primary key binding

                        self.add_subblock(block)
                        idx += len(block.seq())

                except IndexError, BlockLeaderError:
                    pass
            else:
                raise PGPKeyMsgError("First block to key message must be primary or secret key.")

    def add_block(self, block):
        """Add a block to the key message.

        :Parameters:
            - `block`: `Block` instance

        This is a convenience method that will add/replace the primary
        block or a subblock automatically.
        """
        if block.type in [PKT_PUBLICKEY, PKT_PRIVATEKEY]:
            self.new_primary(block)
        else:
            self.add_subblock(block)

    def add_sig(self, sigpkt, target):
        """Add a signature to one of the message's key blocks.

        :Parameters:
            - `sigpkt`: Signature packet instance
            - `target`: string target block leader

        The signature packet's type will indicate the target type (key
        ID or user ID value) and the `target` string will be used to
        distinguish one from the rest. Key IDs are searched first,
        so funky hex user IDs are not encouraged.
        
        :note: For user IDs, `target` is the complete ID string and
            must match exactly.
        """
        block = self.get_block(target)
        block.add_sig(sigpkt)

    def add_subblock(self, block):
        """Add a sub-block to the key message.

        :Parameters:
            - `block`: `Block` instance, of appropriate sub-block type
              (user ID, user attribute, or subkey)

        :note: Adding a block with the same leading user ID or subkey
            as an existing block will replace the existing one.
        :note: User attribute blocks are mindlessly appended, pending
            a *nice* way of distinguishing them.
        """
        block_type = block.type

        if block_type == PKT_USERID:
            self._b_userids[block.leader.body.value] = block

        elif block_type == PKT_USERATTR:
            self._b_userattrs.append(block)

        elif block_type in [PKT_PUBLICSUBKEY, PKT_PRIVATESUBKEY]:
            self._b_subkeys[block.leader.body.id] = block

        else:
            raise NotImplementedError("Sub-block type->(%s) unsupported." % block_type)

    def get_block(self, blocktype, target):
        """Retrieve a key or user ID block given an identifying string.

        :Parameters:
            - `blocktype`: 'key' or 'userid'
            - `target`: string key ID, fingerprint, or (unambiguous) substring
              of a user ID value (for key IDs and fingerprints, make sure that
              `target` is all caps)

        :Returns: `Block` instance or None

        :Exceptions:
            - `PGPKeyMsgError`: multiple user IDs were found, be more
              specific
        """
        target_upper = target.upper()

        if 'key' == blocktype:
            primary = self._b_primary.leader

            if target_upper in [primary.body.fingerprint, primary.body.id]:
                return self._b_primary
            
            for block in self._b_subkeys.values():
                ids = [block.leader.body.fingerprint, block.leader.body.id]

                if target_upper in ids:
                    return block

        elif 'userid' == blocktype:

            for block in self._b_userids.values():

                if target in block.leader.body.value:
                    return block
        
        #if target_upper == self.primary_id:
        #    return self._b_primary
        #
        #if target_upper in self._b_subkeys.keys():
        #    return self._b_subkeys[target]

        #fprint_map = self.map_keyprints()

        #for i in range(len(fprint_map)):

        #    if target_upper == fprint_map[i][0]:
        #        return self._b_subkeys[fprint_map[i][1]]
        #
        #uid_matches = [u for u in self._b_userids.keys() if target in u]

        #if 1 == len(uid_matches):
        #    return self._b_userids[uid_matches[0]]

        #elif 1 < len(uid_matches):
        #    raise PGPKeyMsgError("Target matched multiple user IDs. Be more specific.")

        #return None

    def get_keypkt(self, keyid):
        """Retrieve a particular key from a key message.

        :Parameters:
            - `keyid`: string key ID or fingerprint (20 or 40 char caps hex)
        
        :Returns: key packet or None if not found

        This is just a convenient way to make up for the split between
        the primary key and subkeys in a keymessage.

        :todo: Maybe this should complain if the key isn't found.
        """
        if keyid in [self.primary_id, self.primary_fprint]:
            return self._b_primary.leader

        else:

            for keypkt in [b.leader for b in self._b_subkeys.values()]:

                if keyid in [keypkt.body.id, keypkt.body.fingerprint]:
                    return keypkt

        raise KeyError("No such key: %s" % keyid) # :)

    def list_blocks(self):
        """Retrieve a list of the blocks that make up the key message.

        :Returns: list of block instances
        """
        blocks = [self._b_primary]
        blocks.extend(self._b_userids.list())
        blocks.extend(self._b_userattrs)
        blocks.extend(self._b_subkeys.list())
        return blocks

    def list_keyids(self):
        """Retrieve the entire list of key IDs in a key message.

        :Returns: list of key ID strings

        Since the primary key and subkeys are in different blocks,
        this function allows an easy check to see if a key ID exists
        in a key message at all.
        """
        return [self.primary_id] + self._b_subkeys.keys()

    def map_keyprints(self):
        """Retrieve the list of key fingerprints in a key message.

        :Returns: list of tuples [(key fingerprint, key ID), ..]

        The primary key will always be first in the list.
        """
        fprint_map = [(self._b_primary.leader.body.fingerprint,
                       self._b_primary.leader.body.id)] 
        for subkey_block in self._b_subkeys.list():
            fprint_map.append((subkey_block.leader.body.fingerprint,
                               subkey_block.leader.body.id))
        return fprint_map

    def new_primary(self, block):
        """Set the key message's primary key block.

        :Parameters:
            - `block`: `Block` instance, should be a public key or
              secret block

        :Exceptions:
            - `PGPKeyMsgError`: improper block type (check leader)
        """
        if block.type in [PKT_PUBLICKEY, PKT_PRIVATEKEY]:
            self._b_primary = block
            self.primary_id = block.leader.body.id
            self.primary_fprint = block.leader.body.fingerprint

        else:
            raise PGPKeyMsgError("Primary key block must lead with a public or secret key packet.")

    # user ID and attribute order may change from original (draft allows mixed)
    def seq(self):
        """Retrieve the key message's packet sequence.

        :Returns: list of packet instances
        """
        pkts = self._b_primary.seq()         # primary block
        for block in self._b_userids.list(): # user IDs
            pkts.extend(block.seq())
        pkts.extend(self._b_userattrs)       # user attributes
        for block in self._b_subkeys.list(): # subkeys
            pkts.extend(block.seq())
        return pkts

class SecretKeyMsg(PublicKeyMsg):
    """Secret Key Message

    :IVariables:
        - `primary_key`: PublicKeyBody or SecretKeyBody instance, "primary" key
        - `_b_primary`: block
        - `_b_userids`: list of blocks
        - `_b_userattrs`: list of blocks
        - `_b_subkeys`: list of blocks
        - `_seq`: list of items in message sequence
        - `_d`: string of data used to build message
    
    :CVariables:
        - `type`: constant MSG_PRIVATEKEY (see OpenPGP.constant.messages)
    """
    type = MSG_PRIVATEKEY

class StoredKeyMsg(SecretKeyMsg):
    """Stored Key Message

    :IVariables:
        - `primary_key`: PublicKeyBody or SecretKeyBody instance, "primary" key
        - `_b_primary`: block
        - `_b_userids`: list of blocks
        - `_b_userattrs`: list of blocks
        - `_b_subkeys`: list of blocks
        - `_seq`: list of items in message sequence
        - `_d`: string of data used to build message
    
    :CVariables:
        - `type`: constant MSG_STOREDKEY (see OpenPGP.constant.messages)
    """
    type = MSG_STOREDKEY

class Block:
    """Key Block

    :IVariables:
        - `type`: integer leader packet type constant
        - `leader`: key type packet instance (public/secret key, subkeys)
        - `local_revocs`: list of `OpenPGP.packet.Signature.Signature`
          instances, local revocation signatures
        - `local_bindings`: list of `OpenPGP.packet.Signature.Signature`
          instances, local binding/certification signatures
        - `local_direct`: list of `OpenPGP.packet.Signature.Signature`
          instances, local direct signatures
        - `foreign_revocs`: list of `OpenPGP.packet.Signature.Signature`
          instances, foreign revocation signatures
        - `foreign_bindings`: list of `OpenPGP.packet.Signature.Signature`
          instances, foreign binding/certification signatures
        - `foreign_direct`: list of `OpenPGP.packet.Signature.Signature`
          instances, foreign direct signatures
        - `trust`: list of Trust instances
        - `_seq`: list of packet instances comprising the block

    :CVariables:
        - `none`: none

    :note: `foreign_revocs`, `local_revocs`, etc. are simple packet
        lists and are not meant to imply anything (other than that they
        exist in the given block). In particular, foreign revocations
        and certifications do not necessarily exist with the blessing
        of any local permission. Therefore, just because a foreign
        revocation signature exists and verifies against a foreign key
        does not mean the local key is revoked; permission must first
        be established.
    """
    # TODO require primary_id only if leader not [PKT_PUBLICKEY, PKT_PRIVATEKEY]
    def __init__(self, primary_id, *args, **kwords):
        """Initialize a key block.

        :Parameters:
            - `primary_id`: string primary key ID of key message

        :Keywords:
            - `idx`: integer, if sent a list of packets as the second
              parameter, this is where the block will begin

        :Exceptions:
            - `BlockSubkeyBindingError`: subkey is missing a local
              binding
            - `BlockLeaderError`: block leader is of inappropriate type

        :note: The primary key ID is needed so that the block instance
            can categorize/distinguish local and foreign signatures (see
            `add_sig()`).
        """
        self.primary_id = primary_id
        self.leader = None
        self.local_revocs, self.foreign_revocs = [], []
        self.local_direct, self.foreign_direct = [], []
        self.local_bindings, self.foreign_bindings = [], []
        self.trust = []

        try:
            pkts = args[0]
        except IndexError:
            return

        idx = kwords.get('idx') or 0

        block_pkts = [PKT_PUBLICKEY, PKT_PUBLICSUBKEY, PKT_PRIVATEKEY,
                     PKT_PRIVATESUBKEY, PKT_USERID, PKT_USERATTR]

        if pkts[idx].tag.type in block_pkts:
            self.new_leader(pkts[idx])
            idx += 1

            while 1:

                try:
                    pkt = pkts[idx]
                except IndexError:
                    break

                if pkt.tag.type == PKT_SIGNATURE:
                    self.add_sig(pkt)
                elif pkt.tag.type == PKT_TRUST:
                    self.add_trust(pkt)
                else:
                    break

                idx += 1

            # (only) public subkeys require at least one cert
            if self.type == PKT_PUBLICSUBKEY and 0 == len(self.local_bindings):
                raise PGPBlockSubkeyBindingError("Public subkey block has no local binding.")
        else:
            raise PGPBlockLeaderError("Unacceptable block leader.")

    def add_sig(self, sigpkt):
        """Add a signature to the block.

        :Parameters:
            - `sigpkt`: `OpenPGP.packet.Signature.Signature` instance

        :Exceptions:
            - `BlockError`: primary ID is not set yet

        The type of the signature packet automatically determines which
        signature list it gets placed in (`local_revocs`,
        `foreign_direct`, etc.).
        """
        if self.primary_id: 

            if self.type in [PKT_PUBLICKEY, PKT_PRIVATEKEY]:
                revoker_code = SIG_KEYREVOC
                binding_codes = [] # ensure subkey binding sigs are rejected..

            elif self.type in [PKT_PUBLICSUBKEY, PKT_PRIVATESUBKEY]:
                revoker_code = SIG_SUBKEYREVOC
                binding_codes = [SIG_SUBKEYBIND] # ..in primary key blocks

            elif self.type in [PKT_USERID, PKT_USERATTR]:
                revoker_code = SIG_CERTREVOC
                binding_codes = [SIG_GENERIC, SIG_PERSONA, SIG_CASUAL,
                                 SIG_POSITIVE]

            if revoker_code == sigpkt.body.type:
                if sigpkt.body.keyid == self.primary_id:
                    self.local_revocs.append(sigpkt)
                else:
                    self.foreign_revocs.append(sigpkt)

            elif SIG_DIRECT == sigpkt.body.type:
                if sigpkt.body.keyid == self.primary_id:
                    self.local_direct.append(sigpkt)
                else: 
                    self.foreign_direct.append(sigpkt)

            elif sigpkt.body.type in binding_codes:

                if sigpkt.body.keyid == self.primary_id:
                    self.local_bindings.append(sigpkt)
                else: # not sure what a foreign binding is, but seems illegal
                    self.foreign_bindings.append(sigpkt) # ..(dig through draft)
            else:
                raise NotImplementedError("Sig type->(%s) not supported in this block." % sigpkt.body.type)
        else:
            raise PGPBlockError("Set primary key ID before block signatures.")

    def add_trust(self, trustpkt):
        """Add a trust packet to the trust list.

        :Parameters:
            - `trustpkt`: `OpenPGP.packet.Trust.Trust` instance
        """
        self.trust.append(trustpkt)

    def get_sigs(self):
        """Retrieve all the signatures in the block.

        :Returns: list of signature packets.

        Signature order

            - local revocations (``local_revocs``)
            - foreign revocations (``foreign_revocs``)
            - local bindings/certifications (``local_bindings``)
            - foreign bindings/certifications (``foreign_bindings``)
            - local direct signatures (``local_direct``)
            - foreign direct signatures (``foreign_direct``)
        """
        sigs = []
        sigs.extend(self.local_revocs)
        sigs.extend(self.foreign_revocs)
        sigs.extend(self.local_bindings)
        sigs.extend(self.foreign_bindings)
        sigs.extend(self.local_direct)
        sigs.extend(self.foreign_direct)
        return sigs

    def new_leader(self, pkt):
        """Set the block leader.

        :Parameters:
            - `pkt`: packet instance of appropriate type (primary key,
              subkey, user ID, or user attribute)

        :Returns: None
        """
        self.leader = pkt
        self.type = pkt.tag.type

    def seq(self):
        """Return the sequence of packets used to build block.

        :Returns: list of packet instances
        """
        seq = [self.leader]
        seq.extend(self.get_sigs())
        seq.extend(self.trust)
        return seq

