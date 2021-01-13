# lc2anki

lc2anki is a tool generating Anki cards for LeetCode.

Card template from: <https://github.com/invzhi/LeetCode>

## Usage

### 1. Generate cards

```sh
$ python3 lc2anki.py -h
usage: lc2anki [OPTION]...

lc2anki is a tool generating Anki cards for LeetCode.

optional arguments:
  -h, --help            show this help message and exit
  -l LANG, --lang LANG  specify language, for example: C, C++, Java
  -o FILE, --output-file FILE
                        set output file
  -d, --debug           show debug info

question options:
  -u URL, --url URL     generate cards from link, for example: https://leetcode.com/tag/array/, https://leetcode.com/problemset/top-100-liked-
                        questions/, https://leetcode.com/list/foobar/
  -q [QUESTION ...], --question [QUESTION ...]
                        specify question id or title slug, for example: 1, two-sum, 1-100
  -i FILE, --input-file FILE
                        specify question ids or titles from FILE split by lines
```

#### Examples

From url:

```sh
$ python3 lc2anki.py --lang Python3 --url https://leetcode.com/problemset/top-100-liked-questions/
$ python3 lc2anki.py -l Java -u https://leetcode.com/tag/array/
```

From specific questions:

```sh
$ python3 lc2anki.py --question 1
$ python3 lc2anki.py -q 1 2 3
$ python3 lc2anki.py -q 1-100
$ python3 lc2anki.py -q 1 2 3-100
$ python3 lc2anki.py -q two-sum
$ python3 lc2anki.py -q "Add Two Numbers"
$ python3 lc2anki.py -q two-sum "Add Two Numbers" 3-100
```

From questions in file:

```sh
$ cat q.txt
two-sum
Add Two Numbers
3-100
$ python3 lc2anki.py -i q.txt
```

### 2. Add note type

Add new note type "LeetCode".

Set card template with [front template](template/front-template.html), [back template](template/back-template.html) and [styling](template/styling.css).

Set fields:

![](fields.png)

### 3. Import cards

![](import.png)
