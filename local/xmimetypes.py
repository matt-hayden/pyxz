import mimetypes

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
types_map['.wmv']='audio/x-ms-wmv'