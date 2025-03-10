import sys

if len(sys.argv) == 2:
    sys.exit('usage:./hw3_tester.py <CASE-INDEX>')

with open("result.txt", 'a') as result_file:
    try:
        import hw3
    except:
        result_file.write("GRADE: 0\n")
        sys.exit("module cannot be imported")

    inputs = [(["h(A,f(t))","i(z)+~h(z,f(B))","~i(y)+j(y)"],["~j(A)"]),
              (["h(A,f(t))","i(z)+~h(z,f(B))","~i(y)+j(y)"],["j(A)"]),
              (["feathers(Tweety)", "~feathers(x)+bird(x)"],["~bird(Tweety)"]),
              (["father(Ali,Huseyin)","alive(Ali)","~father(x,y)+parent(x,y)","~parent(x,y)+~alive(x)+older(x,y)"],["~older(Ali,Huseyin)"]),
              (["know(John,x)","know(y,James)"],["~know(John,James)"]),
              (["know(y,James)","know(John,x)"],["~know(John,James)"]),
              (["p(A,f(t,B))", "q(z,C)+~p(z,f(D,u))", "~q(x,y)+r(x,y)"],["~r(A,C)"]),
              (["~prod(x,y,z)+isOne(x)+greaterOrEqual(z,y)","prod(Two,Three,Six)", "~isOne(Two)"],["~greaterOrEqual(Six,Three)"])]
    outputs = [("yes", ["~j(A)$~i(y)+j(y)$~i(A)","~i(A)$i(z)+~h(z,f(B))$~h(A,f(B))","~h(A,f(B))$h(A,f(t))$empty"]),
    		   ("no", []),
               ("yes", ["~bird(Tweety)$~feathers(x)+bird(x)$~feathers(Tweety)","~feathers(Tweety)$feathers(Tweety)$empty"]),
               (('yes', ['~older(Ali,Huseyin)$~parent(x,y)+~alive(x)+older(x,y)$~parent(Ali,Huseyin)+~alive(Ali)', '~parent(Ali,Huseyin)+~alive(Ali)$alive(Ali)$~parent(Ali,Huseyin)',
               '~parent(Ali,Huseyin)$~father(x,y)+parent(x,y)$~father(Ali,Huseyin)', '~father(Ali,Huseyin)$father(Ali,Huseyin)$empty'])),
               ('yes', ['~know(John,James)$know(John,x)$empty']),
               ('yes', ['~know(John,James)$know(y,James)$empty']),
               ('yes', ['~r(A,C)$~q(x,y)+r(x,y)$~q(A,C)', '~q(A,C)$q(z,C)+~p(z,f(D,u))$~p(A,f(D,u))', '~p(A,f(D,u))$p(A,f(t,B))$empty']),
               ('yes', ['~greaterOrEqual(Six,Three)$~prod(x,y,z)+isOne(x)+greaterOrEqual(z,y)$~prod(x,Three,Six)+isOne(x)', 
               	'~prod(x,Three,Six)+isOne(x)$prod(Two,Three,Six)$isOne(Two)', 'isOne(Two)$~isOne(Two)$empty'])]

    i = int(sys.argv[1])
    case_point = 100 / len(inputs)

    try:
        base, goal = inputs[i]
        student_result = hw3.theorem_prover(base,goal)
        if student_result == outputs[i]:
            result_file.write("CASE " + str(i) + ": [OK]\n")
        else:
            result_file.write("CASE " + str(i) + ": [FAILED]\n")
            result_file.write('\tACTUAL:' + str(student_result) + '\n')
            result_file.write('\tEXPECTED:' + str(outputs[i]) + '\n')
    except:
        result_file.write("CASE " + str(i) + ": [FAILED with EXCEPTION]\n")
