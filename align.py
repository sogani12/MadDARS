import sequence_graph
import submatrix
import re
import json
from jinja2 import Template
import naman_to_rutuja as ntr

def align(courses):
    
    result = align_with_majors(courses)
    print(result)
    pretty = prettify_results(result)
    
    return pretty

def prettify_results(result):
    sequences = [item[1] for item in result]
    return generate_html(result)

# Function to generate the HTML and CSS
def generate_html(sequences):
    html_template = Template("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Course Sequence Alignment</title>
        <style>
            body { font-family: Arial, sans-serif; }
            h2 { cursor: pointer; padding: 10px; background: #444; color: white; margin-top: 10px; }
            .program { display: none; padding: 0 15px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .matched { background-color: #c3e6cb; } /* Light green for matched courses */
            .gap { background-color: #f5c6cb; } /* Light red for gaps */
            .legend { margin: 20px 0; }
            .legend div { display: inline-block; padding: 5px 10px; margin-right: 10px; color: white; }
            .matched-legend { background-color: #c3e6cb; }
            .gap-legend { background-color: #f5c6cb; }
        </style>
    </head>
    <body>

    <h1>Course Sequence Alignments</h1>
    <div class="legend">
        <div class="matched-legend">Matched Course</div>
        <div class="gap-legend">Gap / Unique Course</div>
    </div>

    {% for program_name, courses in programs %}
        <h2 onclick="toggleProgram('{{ loop.index }}')">{{ program_name }}</h2>
        <div class="program" id="program-{{ loop.index }}">
            <table>
                <thead>
                    <tr>
                        <th>Course 1</th>
                        <th>Course 2</th>
                    </tr>
                </thead>
                <tbody>
                    {% for course1, course2 in courses %}
                        <tr>
                            <td class="{{ 'matched' if course1 == course2 and course1 != '-' else 'gap' }}">{{ course1 }}</td>
                            <td class="{{ 'matched' if course1 == course2 and course2 != '-' else 'gap' }}">{{ course2 }}</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% endfor %}

    <script>
    function toggleProgram(id) {
        var element = document.getElementById("program-" + id);
        if (element.style.display === "none") {
            element.style.display = "block";
        } else {
            element.style.display = "none";
        }
    }
    </script>

    </body>
    </html>
    """)

    # Render HTML with the template and data
    html_content = html_template.render(programs=sequences)
    return html_content
    

def make_student_graph(courses):
    
    l = ["".join(item.split()) for item in courses]
    l.sort(key=lambda item:int(re.findall(r"\d+",item)[0]))
    
    ref = ",".join(l)
 
    student_g = sequence_graph.VariantGraph(ref)
    student_g.reorder_topological()
    return student_g

def align_with_majors(courses):
    
    with open("smalldata.json") as f:
        data = json.load(f)
        
    refs = {}
    subs = {}
    major_classes = {}
    
    for major in data:
        ref, sub, classes = ntr.object_maker(data[major])
        refs[major] = ref
        subs[major] = sub
        major_classes[major] = classes
 
    results = []
    
    print(refs['data-science-bs'])
    print(subs['data-science-bs'])
   
        
    for major in refs:
        
        all_classes = set() 

        major_set = refs[major].split(",")
        for item in subs[major]:
            major_set.extend(item[2].split(","))
            
#         major_classes = list(set(major_classes))
        
#         def sorter(item):
#             finds = re.findall(r"(\D+)(\d+)", item)[0]
#             return (finds[0], int(finds[1]))
            
#         major_classes.sort(key = sorter)

            
        alphabet = {value:key for key, value in enumerate(major_classes[major])}
        
        all_classes.update(major_set)
        
        all_classes.update(["".join(item.split()) for item in courses])
        
        courses = ["".join(item.split()) for item in courses]
        courses = sorted(courses, key=lambda item: alphabet.get(item, 0))
        
        DNA = all_classes
        basic_dna_submatrix = submatrix.match_mismatch_matrix(1, -1, DNA)
        graph = make_student_graph(courses)
        
        major_g = sequence_graph.VariantGraph(refs[major])
        for var in subs[major]:
            major_g.add_complex_variant(*tuple(var))
        major_g.reorder_topological()
        _, out = align_graphs(graph, major_g, basic_dna_submatrix, 0)
        results.append((major,out))
         
    return results
            
            
            
def align_graphs(x, y, substitution_matrix, s):
    
    assert x.is_valid(), "sequence graph x is not valid"
    assert y.is_valid(), "sequence graph y is not valid"
    
    n = x.num_vertices()
    m = y.num_vertices()  

    M = matrix(n, m)
    t = matrix(n, m)
    
    M[0][0]=0
    
    for i in range(1, n):
        parents = [(M[k][0]+s, (k,0)) for k in sorted(x.parents(i), reverse=True)]
        M[i][0], t[i][0] = max(parents)
        
    for j in range(1, m):
        parents = [(M[0][l]+s, (0,l)) for l in sorted(y.parents(j), reverse=True)]
        M[0][j], t[0][j] = max(parents)
        
    
    for i in range(1, n-1):
        for j in range(1, m-1):
            vals1 = []
            for k in sorted(x.parents(i), reverse=True):
                for l in sorted(y.parents(j), reverse=True):
                    vals1.append((M[k][l] + substitution_matrix[x.vertex_label(i), y.vertex_label(j)], (k,l)))
                    
            val1 = max(vals1)
            vals2 = [(M[k][j]+s, (k, j)) for k in sorted(x.parents(i), reverse=True)]
            val2 = max(vals2)
            vals3 = [(M[i][l]+s, (i, l)) for l in sorted(y.parents(j), reverse=True)]
            val3 = max(vals3)
            vals = sorted([val1, val2, val3], key=lambda item:item[1], reverse=True)
            M[i][j], t[i][j] = max(vals)
    
    vals = []
    for k in x.parents(n-1):
        for l in y.parents(m-1):
            vals.append((M[k][l], (k,l)))
    M[n-1][m-1], t[n-1][m-1] = max(vals)
    
    x_result = ""
    y_result = ""
    i, j = n-1,m-1
    
    pairs = []
    while i or j:
        traceback = t[i][j]
        p, q = traceback
                    
        if p == i:
            pairs.append(("-", y.vertex_label(j)))
        
        elif q == j:
            pairs.append((x.vertex_label(i), "-"))
            
        else:
            pairs.append((x.vertex_label(i) or "-", y.vertex_label(j) or "-"))
            
        while j-q > 1:
            j -= 1

        
        while i-p > 1:
            i -= 1

                
        i = p
        j = q
    
    pairs.reverse()
    pairs = pairs[:-1]    
    
    return (M[n-1][m-1], pairs) #transpose_alignment(pairs))
    
def matrix(num_rows, num_cols, initial_value=None):
    """Returns a matrix (a list of rows, each of which is a list) 
    with num_rows and num_cols and with initial_value in each entry"""
    return [[initial_value] * num_cols for i in range(num_rows)]

def transpose_alignment(alignment):
    """Returns a column-based alignment from a row-based alignment or vice versa"""
    return list(map(''.join, zip(*alignment)))   