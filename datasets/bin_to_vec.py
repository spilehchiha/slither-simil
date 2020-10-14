from fasttext import load_model
import argparse
import errno

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=("Print fasttext .vec file to stdout from .bin file")
    )
    parser.add_argument(
        "model",
        help="Model to use",
    )
    args = parser.parse_args()

    f = load_model(args.model)
    words = f.get_words()
    print(str(len(words)) + " " + str(f.get_dimension()))
    for w in words:
        v = f.get_word_vector(w)
        vstr = ""
        for vi in v:
            vstr +=  str(vi) + "\t"
            #vstr += " " + str(vi)
        try:
            #print(w + vstr)
            #print(w)
            print(vstr)
        except IOError as e:
            if e.errno == errno.EPIPE:
                pass
