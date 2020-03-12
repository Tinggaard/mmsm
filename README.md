# Matador-Mix-Sorterings-Maskine (MMSM)
Et eksamensprojekt i Teknikfag A (EL) på Odense Tekniske Gymnasium af Nikolai Prip og Jens Tinggaard.

Projektet tager udgangspunkt i projektoplæg 1: Styring, automatisering og overvågning.
I dette repo ligger kildekoden brugt til at lave computervision, som en del af projektet.


## Forudsætninger
Forud for installering, skal [Python 3](https://python.org/downloads) være installeret.
### step 1
Klon dette repo, eller download det [her](https://github.com/Tinggaard/mmsm/archive/master.zip)
```shell
$ git clone https://github.com/Tinggaard/mmsm.git
```

### step 2
Opret et virtual environment og installer pakker
```shell
$ cd mmsm
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Brug
Inden programmet køres, gøres filen executable
```shell
$ cd src
$ chmod +x main.py
```
Dernæst køres programmet som følger:
```shell
$ ./main.py [billedfil]
```
F.eks.
```shell
$ ./main.py ../img/5.jpg
```


### Licens
Al koden er licenseret under [MIT licensen](https://github.com/Tiggaard/mmsm/blob/master/LICENSE).
