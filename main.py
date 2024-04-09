from time import sleep

CHARACTER_LIMIT = 32


def main():
    with open('text.txt') as f:
        text = f.read()

    sentences = text.split('. \n')

    print(sentences)

    for sentence in sentences:
        words = sentence.split(' ')
        print_words(words)


def print_words(words):
    words_to_be_printed = ""
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 <= CHARACTER_LIMIT:
            current_length += (len(word) + 1)
            words_to_be_printed += word
            words_to_be_printed += ' '
        else:
            print(words_to_be_printed)
            sleep(3)
            words_to_be_printed = ""
            words_to_be_printed += word
            words_to_be_printed += ' '
            current_length = len(word) + 1

    print(words_to_be_printed)
    sleep(3)


if __name__ == '__main__':
    main()
