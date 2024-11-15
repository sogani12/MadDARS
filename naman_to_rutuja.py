import re
from itertools import combinations

def object_maker(data):
    l = list_maker(data)
    s = string_maker(l)
    return s

def grab_key(data):
    if isinstance(data, str):
        return int(re.findall(r"\d+",data)[0])
    if isinstance(data, tuple) and len(data) == 0:
        return 999
    return grab_key(data[0])

def list_maker(d):
    major = []
    for val in d.get("h1", []):
        major.append(val)

    for h in [item for item in d.keys() if item.startswith("h2")]:
        num = d[h]['80']
        temp_c = set()
        if len(d[h]['2']) >= 1:
            major.append(tuple(d[h]['2']))
            for val in d[h]['2']:
                temp_c.update(val)
#         if len(set(d[h]['1']) - temp_c):
#             l = list(combinations(set(d[h]['1'])-temp_c,num))
#             val = tuple(sorted(l))
#             major.append(val)
        if len(d[h]['2']) == 0 and len(d[h]['1']) > 0:
            l = list(combinations(d[h]['1'],num))
#             val = tuple(sorted(l))
            major.append(l)
            
        elif num == 1:
            l = list(combinations(d[h]['1'],num))
            val = tuple(sorted(l))
            major.append(val)
            
    major = sorted(major, key=lambda item: grab_key(item))
    return major

def clean_key(string):
    i = re.findall(r"(\D+)(\d+)", string)[0]
    key = sorted(i[0].split("/"))[0]
    code = i[1]
    return key+code

def string_maker(major):
    refl = []
    subl = []
    courses = set()
    ref_idx = 0
    courselist = []

    for course in major:
        if isinstance(course, str):
            courses.add(course)
            courselist.append(course)
            refl.append(course)
            ref_idx += 1
        else:
            sub = []
            add_sub = False
            for path in course:
                if not add_sub:
                    hits = 0
                    for c in path:
                        if c in courses:
                            hits += 1
                    if hits == 0:
                        refl.append(path)
                        courses.update(path)
                        courselist.extend(path)
                        add_sub = True
                        ref_idx+=1
                        length = len(path)
                    else:
                        sub.append(path)
                else:
                    sub.append(path)
            subl.append((ref_idx+1, length, tuple(sub)))
#     refl = []
#     subl = []
#     courses = set()
#     courselist = []
#     ref_idx = -1
#     incr = 1
    
#     for course in major:
#         if isinstance(course, str):
#             courses.add(course)
#             courselist.append(course)
#             refl.append(course)
#             ref_idx += 1
#             incr=1
#         else:
#             sub = []
#             add_sub = False
#             for path in course:
#                 if not add_sub:
#                     hits = 0
#                     for c in path:
#                         if c in courses:
#                             hits += 1
#                     if hits == 0:
#                         refl.append(path)
#                         courses.update(path)
#                         courselist.extend(path)
#                         add_sub = True
#                         ref_idx+=incr
#                         length = len(path)
#                         incr=length
#                     else:
#                         sub.append(path)
#                 else:
#                     sub.append(path)
#             subl.append((ref_idx+1, length, tuple(sub)))
            
#     print(refl)
            
    ref = []
    for r in refl:
        if isinstance(r, str):
            ref.append(clean_key(r))
        else:
            for i in r:
                ref.append(clean_key(i))

    ref = ",".join(ref)
    variants = []

    for pos, length, sub in subl:
        for s in sub:
            variants.append((pos, length, ",".join(s)))
            
    return (ref, variants, list(set(courselist)))
