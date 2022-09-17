import random

cypher = {'a': ['187fx', '46ahl', '0gr2t', 'emdik', 'c8fgr', 'cl5z2', '6f7ik', '4o0nx', 'ss4hp', 'cygvv'],
          'b': ['2oobd', 'tdf4b', 'yl6qb', '35o0v', 'jzimj', '57wfr', 'dmqeu', '5p7qu', 'rinoh', 'qrutq'],
          'c': ['q9dud', '8sdfn', 'ko9sb', 'b6g37', '2y0wk', 'fjkm5', '1dvrb', 'c1tnb', 'b3ju9', 'fvn0v'],
          'd': ['r4jkz', '5vz5r', 'b2kqu', 'r4rff', 'zpesq', 'tzl63', 'kib0x', 'y62ua', 'rikfw', 't48pj'],
          'e': ['z5int', 'jnxxe', 'mx8gu', 'g6k7n', 'qe0t7', 'ea3u9', 'lg3kv', '6262u', 'nli9l', 'x6iqa'],
          'f': ['26g2g', 'vcrkx', 'semwr', 'hnx0h', 'emwe7', 'c6s98', 'mf97k', 'pikuq', 'vwc62', '83zuj'],
          'g': ['m9lho', '810vt', 'uk82e', 'somh4', 'i7wo6', '0tol7', '6lsyh', 'i4zt5', 'zgnk4', 'jjkmb'],
          'h': ['y6jmp', 'r3g3g', '6hllr', 'e75q7', 'xev31', '6uad5', 'sds9z', 'o2md2', 'tstki', 'p79s7'],
          'i': ['we3bq', 'kt7rl', 'o5mac', '57715', 'v8x5e', '77dro', 'q9edx', 'nk0zl', 'c4qae', 'cxfrt'],
          'j': ['i4irc', 'uldad', 'jvl33', '7bwjz', 'ne4w3', '8o9q9', '4zvhv', '1rhxb', 'ugpvt', '2qaln'],
          'k': ['t6poi', 'rs1eg', 'wjidy', 'ld8v8', 'fzw7f', '5iu21', 'kh2wg', 'bjv4r', '7ri4t', 'jgq3y'],
          'l': ['sx0na', 'wiuv1', 'uykcd', 'o60l2', '7tb7t', '06v48', 'kv4qa', '3p788', 'hhs0w', '87tcu'],
          'm': ['3bk8o', 'h2kzl', 'rajrm', 'llqj1', '4g97a', '0tzbr', 'iy95w', 'elk8n', 'xs7oo', '7zf54'],
          'n': ['q4jgj', 'ycbpn', 'ax118', '0z9bk', 'xbcxa', '608ft', 'ls512', 'ufano', 'f0kgn', 'qiap0'],
          'o': ['achj5', '7kenp', '42w3l', 'gutp5', 'zw95p', 'jqvzu', 't6bfg', 'nboev', 'i0f7u', 'l0glk'],
          'p': ['8whqj', 'c6nyc', '68bfb', 'jeedg', 'xwi2j', 'tfw82', '3piic', 'x0ajr', '1885r', '4an76'],
          'q': ['zh8l2', 'fgjd8', 'rrz4k', 'xa0uo', 'wt9d1', 'uiwzz', 'zzyqf', '5i99t', 'f9tkz', '6088m'],
          'r': ['e3zmd', '3ku4j', 'dxp5t', 'hwdat', 'b6l6s', 'yy1bj', 'e1oz4', 'bgq5w', 'htas7', '3wf0a'],
          's': ['jza8j', 'lv7q7', '8ofwu', 'tioet', '8zaaq', 'wtvl8', 'w6xgy', 'la2dp', 'eg8pr', 'qwaec'],
          't': ['7dqi5', 'fyl9l', 'x2quz', '4fdy2', 'qr34g', '8kff3', 'njnb7', 'qwrbh', '9qu8c', 'wgnex'],
          'u': ['dup8g', 'm9hhr', '5we3r', 'is007', 'xmdun', 'ewjj8', 'v2epa', 's3dnd', 'mwb4d', 'fsfmw'],
          'v': ['0g2qn', 'gkr1l', 'ujss0', 't7h85', 'o2eub', 'jmlaw', '2a3a6', '0szzg', '21kkq', '6jvhy'],
          'w': ['yjh73', 't8bvc', 'dthr4', 'f50o7', 'leqg8', 'mvs8t', 'zv6tb', 'dyroh', '8t0md', 'gy5be'],
          'x': ['rs16n', 'vbv3f', 'lfvvc', 'g8h5q', 't7qsp', '8p4ce', 'zh5dk', 'wur9v', 'epzvj', '6uma7'],
          'y': ['5q207', 'favcn', 'tove2', 'zkfx9', 'd2nvw', 'd1piz', 'pqmv8', '0wss1', 'up6aj', '75ahn'],
          'z': ['gj9dy', 'ywrcg', 'b2xdf', 'qkh2j', '8v84h', 'baz0h', 't9p2a', 'hjrhg', '168a2', 'jz2xb'],
          '0': ['6kb0f', 'fu2j3', 'btj89', 'cdliz', 'qc0ek', 'k9arw', 'bmh4k', 'mno5s', 'n6ntq', '6pjbv'],
          '1': ['o2gx9', 'zzc95', '2hg0y', 're65y', '0ifef', 'lcty0', 'urgek', '9oxlr', 'cecfn', 'szr9f'],
          '2': ['phrn0', 'c6pur', 'zli9t', '4h2lv', 'o1pyn', 'rl7sl', 'r7n4c', 'i0zos', 'yj8za', 'si3e1'],
          '3': ['t60rr', 'txfyu', 'furz9', 'rrbdi', 'ai4ta', 'r38lb', 'iwm8v', 'sj2gv', '9fp8r', '5rqsl'],
          '4': ['nk705', 'yqx13', '35buw', 'bzx50', '1wjho', '27s0s', 'fql52', 'lo0zw', 's67fi', 'v6hj2'],
          '5': ['4etca', 'mclp8', '46g5d', '2dswy', 'j8ieh', 'snkj4', 'yuipj', 'cv9el', 'sw9yn', 'nam7a'],
          '6': ['k8q25', '1zdx9', 's4xv2', 'd9czh', 'cbvba', 'c7fzl', 'vuwzf', '8vq3z', 'f8af3', '67fvc'],
          '7': ['xknga', '53nma', 'hk35l', 'du6mt', '48k0o', 'xdabr', '5cssb', '6hscz', 'pp1ul', 'nxf9c'],
          '8': ['rxj61', 'yg7g3', 'fhv3f', '9qnq8', '93z4k', '1y9f3', '2glex', '49pb7', 'wykdm', 'th6ud'],
          '9': ['bcdg7', 'h2t8a', '9qq1v', 'p91d7', 'dprvg', 'dql7p', 'getcn', 'k874d', 'vrj41', 'gq3na'],
          '.': ['7hg0i', 'h5aq7', 'mrhzv', 'vhnzv', 'reyuc', 'ovzvo', 'ifpeo', 'o9pea', '787x5', '7evr7'],
          '_': ['nlocb', 'l4sw2', 'tr5wc', '8qzs0', 'xakfi', '0hulq', 'iyxsk', 'iks1j', '9owok', '2redf'],
          '@': ['mt2lk', 'pnxbd', 'xzupq', 'y0ado', 'bryfk', 'tl67u', '6j3h7', 'p0t6t', 'bbiix', 'qyyid']}


# code to check repetitions in cypher dict

# final = []
# for i in cypher.values():
#     final.extend(i)
#
# print(len(set(final)))


def encrypt(message):
    encrypted_message = ""
    for i in message:
        rand_substring = random.choices(cypher[i])
        encrypted_message_sub = encrypted_message.join(rand_substring)
        encrypted_message += encrypted_message_sub
    return encrypted_message


def decrypt(message):
    decrypted_message = ""
    split_message = [message[idx:idx + 5] for idx in range(0, len(message), 5)]
    for letter in split_message:
        letter_found = 0
        for key, values in cypher.items():
            if letter in values:
                decrypted_message += key
                letter_found = 1
        if letter_found == 0:
            raise Exception("Cant decrypt message")

    return decrypted_message
