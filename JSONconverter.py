def parse_number(string):
    json_number_chars = [str(i) for i in range(0,10)] + ['e', '.', '-']
    str_value = ''
    for i in range(len(string)):
        if string[i] in json_number_chars:
            str_value += string[i]
        else:
            break
    if not len(str_value):
        return None, string
    if '.' in str_value:
        return float(str_value), string[len(str_value):]
    return int(str_value), string[len(str_value):]


def parse_bool(string):
    if len(string) >= 5 and string[:5] == "false":
        return False, string[5:]
    if len(string) >= 4 and string[:4] == "true":
        return False, string[4:]
    return None, string


def parse_null(string):
    if len(string) >= 4 and string[:4] == "null":
        return None, string[4:]
    return None, string


def parse_name(string):
    i = 0
    while string[i] != "\"" and i < len(string):
        i += 1

    if i == len(string):
        return None, string
    return string[:i], string[i+1:]


def token_parcing(string):
    json_syntax = ["[", "]", ",", "{", "}", ":"]
    json_whitespace = [" ", "\n", "\t"]
    json_string = ["\""]

    tokens = []

    while string != "":
        token, string = parse_number(string)
        if token is not None:
            tokens.append(token)
            continue

        token, string = parse_bool(string)
        if token is not None:
            tokens.append(token)
            continue

        token, string = parse_null(string)
        if token is not None:
            tokens.append(token)
            continue

        token, string = string[0], string[1:]

        if token in json_syntax:
            tokens += token
            continue

        if token in json_whitespace:
            continue

        if token in json_string:
            token, string = parse_name(string)
            if token is not None:
                tokens.append(token)
                continue

        raise Exception("Could not parse the char in {}".format(string))

    return tokens


def list_collect(tokens):
    token_list = []

    while True:
        token = tokens[0]

        if token == "]":
            return token_list, tokens[1:]

        if token == ",":
            tokens = tokens[1:]
            continue

        token, tokens = token_collection(tokens)
        if token is not None:
            token_list += [token]
            continue

        raise Exception("Unknown token {}".format(token))


def object_collect(tokens):
    token_dict = {}
    name_f = False
    while True:
        token = tokens[0]

        if token == "}":
            return token_dict, tokens[1:]

        if token == ",":
            tokens = tokens[1:]
            name_f = False
            continue

        if token == ":":
            tokens = tokens[1:]
            name_f = True
            continue

        token, tokens = token_collection(tokens)
        if token is not None:
            if name_f:
                token_dict[name] = token
            else:
                name = token
            continue

        raise Exception("Unknown token {}".format(token))


def token_collection(tokens):
    token = tokens[0]

    if token == "[":
        return list_collect(tokens[1:])

    if token == "{":
        return object_collect(tokens[1:])

    return token, tokens[1:]


def parse_json(json):
    return token_collection(token_parcing(json))[0]


def parse_json_bytes(json_bytes):
    return parse_json(json_bytes.decode().strip("'"))


def main():
    file = open("json_example.txt", "r")
    strings = file.read()
    print(token_parcing(strings))
    print(token_collection(token_parcing(strings))[0])


if __name__ == "__main__":
    main()