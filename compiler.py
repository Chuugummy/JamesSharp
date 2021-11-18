import sys
import os
import time
import base64
import autopep8

def compile():
    file = sys.argv[2]

    if not os.path.isfile(file):
        print("jspcompiler: ~ File does not exist")
        return

    if not file.endswith(".jsa"):
        print("jspcompiler: ~ Invalid file")
        return

    start_time = time.time()
    print("jspcompiler: ~ Parsing file...")

    with open(file, "r") as f:
        stack = ""
        variables = []
        functions = []

        for line in f:
            def check(line, stack):
                # ~ Type Checks
                if line.startswith("var"):
                    var_name = line.split(" ")[1]
                    if var_name in variables:
                        print("jspcompiler: ~ Variable already declared: " + var_name)
                        sys.exit(1)

                    var_content = line[var_name.__len__() + 4:]

                    if var_content.strip().startswith("\""):
                        variables.append(var_name)
                        stack += var_name + "=" + var_content + "\n"
                    else:
                        _check = check(var_content.strip(), "")
                        stack += var_name + " = " + _check + "\n"

                if line.startswith("//"):
                    pass

                # ~ Switches
                if line.startswith("equal"):
                    _a1 = line.split(" ")[1]
                    _a2 = line.split(" ")[2]

                    statement_body = ""
                    otherwise = ""
                    while not line.startswith("end"):
                        line = f.readline()
                        if line.startswith("end"):
                            break

                        if line.startswith("otherwise"):
                            while not line.startswith("end"):
                                line = f.readline()
                                if line.startswith("end"):
                                    break

                                __data = check(line.strip(), "")
                                otherwise += "\t"+__data + "\n"

                        _data = check(line.strip(), "")
                        statement_body += "\t"+_data + "\n"

                    if otherwise != "":
                        stack += "if " + _a1.strip() + " == " + _a2.strip() + ":\n" + \
                            statement_body + "\nelse:\n" + otherwise + "\n"
                    else:
                        stack += "if " + _a1.strip() + " == " + _a2.strip() + \
                            ":\n" + statement_body + "\n"

                # ~ Function Calls
                if line.startswith("def"):
                    func_name = line.split(" ")[1]
                    args = line[line.index("(") + 1:line.index(")")]
                    _func_name = func_name[:func_name.find("(")]

                    if _func_name in functions:
                        print(
                            "jspcompiler: ~ Function already declared: " + _func_name)
                        sys.exit(1)

                    func_body = ""
                    while not line.startswith("stop"):
                        line = f.readline()
                        if line.startswith("stop"):
                            break

                        _data = check(line.strip(), "")

                        if not _data.startswith("\n"):
                            func_body += "\t" + _data + "\n"
                        else:
                            func_body += ""+_data

                    functions.append(_func_name)

                    func_body = str(autopep8.fix_code(func_body, options={
                        'aggressive': 1, 'indent_size': 4, 'max_line_length': 120}))

                    func_body = func_body.replace("\n", "\n\t")

                    stack += "def {0}({2}):\n{1}\n".format(_func_name.strip(), func_body, args.strip())

                if line.startswith("call"):
                    function_name = line.split(" ")[1].strip()
                    args = line[line.index("(") + 1:line.index(")")]
                    function_name = function_name[:function_name.find("(")]

                    if function_name not in functions:
                        print("jspcompiler: ~ Function not declared:" +
                        function_name)
                        sys.exit(1)

                    stack += "{0}({1})\n".format(function_name, args.strip())

                if line.startswith("stop"):
                    pass

                # ~ Variable Assignments
                if line.startswith("set"):
                    var_name = line.split(" ")[1]
                    if var_name not in variables:
                        print(
                            "jspcompiler: ~ Variable not declared on line " + str(line))
                        sys.exit(1)

                    var_content = line[4:].strip()
                    var_content = var_content[var_name.__len__():]
                    stack += "{0}={1}\n".format(var_name, var_content)

                # ~ Built-in Functions
                if line.startswith("print"):
                    print_content = line[6:].strip()
                    stack += "print({0})\n".format(print_content)

                if line.startswith("input"):
                    input_content = line[6:].strip()
                    stack += "input({0})\n".format(input_content)

                if line.startswith("sleep"):
                    sleep_content = line[6:].strip()
                    stack += "time.sleep({0})\n".format(sleep_content)

                if line.startswith("os.name"):
                    stack += "os.name\n"

                if line.startswith("exit"):
                    stack += "exit()\n"

                return stack

            stack = check(line, stack)

        print("jspcompiler: ~ Checking indentation...")

        print("jspcompiler: ~ Compiling " + file + "...")
        encoded = base64.b64encode(stack.encode()).decode()

        with open(file.replace(".jsa", ".jse"), "w") as f:
            f.write(encoded)

        print("jspcompiler: ~ Compiled in {0} seconds".format(
            time.time() - start_time))

def run():
    file = sys.argv[2]

    if not os.path.isfile(file):
        print("jspcompiler: ~ File does not exist")
        return

    if not file.endswith(".jse"):
        print("jspcompiler: ~ Invalid file")
        return

    print("jspcompiler: ~ Running file...")

    with open(file, "r") as f:
        stack = base64.b64decode(f.read()).decode()
        try:
            exec(stack)
        except Exception as e:
            print("jspcompiler: ~ Error at runtime: " + str(e))

def main():
    switch = sys.argv[1]

    if switch == "-c":
        compile()
    elif switch == "-r":
        run()

    else:
        print("jspcompiler: ~ Invalid argument")
        print("jspcompiler: ~ Usage: jspcompiler [-c] <file> | [-r] <file>")

if __name__ == "__main__":
    main()