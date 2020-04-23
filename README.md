# Matador-Mix-Sorterings-Maskine (MMSM)
Et eksamensprojekt i Teknikfag A (EL) på Odense Tekniske Gymnasium af Nikolai Prip og Jens Tinggaard.

Projektet tager udgangspunkt i projektoplæg 1: Styring, automatisering og overvågning.
I dette repo ligger kildekoden brugt til at lave computervision, som en del af projektet.


## Om
#### Python
Størstedelen af dette repo er brugt til at teste CV i Python, koden findes under [src/](https://github.com/Tinggaard/mmsm/tree/master/src). Samt billederne fra [img/](https://github.com/Tinggaard/mmsm/tree/master/img) og [out/](https://github.com/Tinggaard/mmsm/tree/master/out).


#### Arduino
Derudover ligger den også den smule Arduino kode, som er skrevet (lidt i blinde, grundet mangel af mulighed for at teste det pga. covid-19) i forbindelse med projektet. Arduino koden kan findes under [stepper/](https://github.com/Tinggaard/mmsm/tree/master/stepper).


## Disclaimer
Billederne i [img/](https://github.com/Tinggaard/mmsm/tree/master/img) er forsøg, som er taget inden vi havde fastlagt en model for, hvordan billederne skulle tages i sidste ende. Men da vores værkstedsuge er aflyst pga covid-19, har vi ikke mulighed for at fastlægge andre rammer og der bliver af den grund ikke taget andre billeder. Det har gjort det lidt svært at tage nogle ordentlige billeder, da vi egentlig gerne ville have en anden baggrund end et køkkenbord.


## Forudsætninger
Forud for installering, skal [Python 3](https://python.org/downloads) være installeret.

Nedenstående vejledning tager udgangspunkt i Linux, da det er udviklet på en Linux maskine, dog er de overordnede steps de samme for Windows.


### step 1
Klon dette repo, eller download det [her](https://github.com/Tinggaard/mmsm/archive/master.zip)
```shell
$ git clone https://github.com/Tinggaard/mmsm.git
```

### step 2
Opret et virtual environment og installer pakker
```shell
$ cd mmsm
$ python3 -m venv venv
$ . venv/bin/activate
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

### Om brug
Der vil være on prompt, som beder brugeren om at vælge type slik, som skal frasorteres, efter dette er indtastet, bliver det samlet op. Programmet kan kategorisere slikket som følger: `yellow`, `red`, `green` og `larve`. Det betyder samtidig at nogle af stykkerne slet ikke falder inden for nogen kategori, navnligt de mørke stykker slik.
Derudover gøres der opmærksom på, at det i koden skal opsættes, hvilken port Arduinoen er forbundet til på computeren, samt at projektet ikke har været tesetet i virkeligheden grundet covid-19. Al testing er udelukkende foregået på billede 5.


## Licens
Al koden er licenseret under [MIT licensen](https://github.com/Tinggaard/mmsm/blob/master/LICENSE) af Jens Tinggaard.
