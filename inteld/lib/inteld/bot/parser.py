import re

def getargs(text, argdict):
    """
    Extract arguments in argdict from text.

    An argument is either just the word itself, or the word followed
    by an equal sign and the value. The value can be enclosed in
    quotation marks.

    argdict contains arguments and their default values.

    Returns the text without arguments and a dictionary mapping
    arguments to their values.
    """
    result = {}
    for arg, default in argdict.items():
        text, value = extract_arg(text, arg)
        if value is None:
            result[arg] = default
        else:
            result[arg] = value
    return text, result

def extract_arg(text, argname):
    m = re.search(r"\b(%s)\b" % re.escape(argname),
                  text)
    if m is None:
        return text, None
    ltext = text[:m.start(1)]
    rtext = text[m.end(1):]
    if rtext.startswith('="'):
        try:
            idx = rtext.index('"', 2)
        except ValueError:
            return text, None
        value = rtext[2:idx]
        rtext = rtext[idx+1:]
    elif rtext.startswith("="):
        try:
            idx = rtext.index(' ', 1)
        except ValueError:
            value = rtext[1:]
            rtext = ""
        else:
            value = rtext[1:idx]
            rtext = rtext[idx:]
    else:
        value = True
    return ("%s %s" % (ltext.rstrip(), rtext.lstrip())).strip(), value
