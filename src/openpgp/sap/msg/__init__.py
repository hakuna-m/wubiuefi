"Message support RFC 2440.10"

# TODO OpenPGP Grammar
#
#   What I'd like to do is turn this all into a slick parser, or 
#   convert it to some form that an existing parser can understand. My
#   guess is that doing so would make it much easier to add message
#   types (and packet types) support more complex messages.
#
# TODO pkts integrity
#
#   Right now, pkts is deep-copied to preserve the original on
#   the outside.
#
#   It might be nice to replace the pop() logic in pkts parsing 
#   with the strcalc(func, pkts[idx:idx+n], idx) deal used 
#   in packet parsing (advantages: speed?) and no need to make
#   copies of outside the pkts). Either that or..
#
#   Things are a little off-kilter in that the pkts is
#   manipulated via functions instead of manipulating itself (like
#   with list.pop()). One solution would be to extend list 
#   functionality with a PacketList class that defined a organize_msgs
#   method similar to pop().
#
# TODO nested messages
#
#   The way things work now, messages are built up like this -
#
#   For a particular message pattern:
#   1) see if the packet falls in line with the message pattern (if
#   so, keep it, if not, ditch it and fail) 2) if the pattern accepts
#   a nested message, recurse the pattern search and add the nested
#   message instance 3) see if the message pattern has been matched
#   (if so, return, if not, repeat)

