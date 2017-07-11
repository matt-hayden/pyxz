import mimetypes
"""Monkey-patch the built-in mimetype map with some common missing pieces.
"""

_types_map = mimetypes.types_map

types_map = _types_map.copy()
types_map['.cda']='audio/raw-cd'
types_map['.flac']='application/ogg'
types_map['.m4a']='audio/mp4'
types_map['.m4p']='audio/x-m4p'
types_map['.m4v']='video/m4p'
types_map['.mpeg']='video/mpeg'
types_map['.ogg']='application/ogg'
types_map['.rar']='application/x-rar-compressed'
types_map['.wma']='audio/x-ms-wma'
types_map['.wmv']='video/x-ms-wmv'
types_map['.asf']='video/x-ms-asf'

types_map['.rmvb']='application/vnd.rn-realmedia-vbr'
types_map['.flv']='video/x-flv'

types_map['.mka']='audio/x-matroska'
types_map['.mkv']='video/x-matroska'
types_map['.mk3d']='video/x-matroska-3d'

types_map['.psd']='image/vnd.adobe.photoshop'
types_map['.jps']='image/x-jps'

types_map['.bash']='application/x-bash'

# guesses:
types_map['.avs']='text/x-avisynth'
types_map['.json']='text/json'
types_map['.m3u']='text'
