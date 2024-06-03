from db import DB
import pandas as pd
import io
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-v0_8-poster')


MCOLOR = '#6488EA'
FCOLOR = '#FDB0C0'

db = DB()
db.connect()
ageList = ['(0-2)', '(4-6)', '(8-12)', '(13-17)', '(18-24)',
           '(25-32)', '(38-43)', '(48-53)', '(60-100)']


def __getDF() -> pd.DataFrame:
    df = pd.DataFrame(db.fetchAll(), columns=[
        "ID", "Camera", "Age", "Gender", "Datetime"])

    df['Age'] = pd.Categorical(df['Age'], categories=ageList, ordered=True)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df = df.sort_values('Age')

    return df


def __plt2Bytes(plt) -> io.BytesIO:
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    return buffer


def getGenders() -> dict[str, int]:
    genders = __getDF().Gender.value_counts()
    return dict(genders)


def getAges() -> dict[str, int]:
    ages = __getDF().Age.value_counts()
    ages = dict(sorted(ages.items()))
    return ages


def __display(plot: io.BytesIO):
    img = plt.imread(plot)
    plt.imshow(img)
    plt.axis("off")
    plt.legend().remove()
    plt.show()


def getDataInfo() -> dict:
    df = __getDF()

    info: dict = {
        "totalRecord": df.Age.count(),
        "maleCount": df.query("Gender == 'Male'").Gender.count(),
        "femaleCount": df.query("Gender == 'Female'").Gender.count(),
        "firstRecord": df.sort_values("Datetime", ascending=True).iloc[0, 4].strftime("%Y-%m-%d %H:%M:%S"),
        "lastRecord": df.sort_values("Datetime", ascending=False).iloc[0, 4].strftime("%Y-%m-%d %H:%M:%S")
    }
    return info


def getAgesPiePlot(useGradientColor: bool = False) -> io.BytesIO:
    ages = __getDF().Age.value_counts()
    ages = ages[ages.values > 0]
    plt.figure(figsize=(8, 8))
    plt.title("Ages")

    colors = ['#C2F0C2', '#A3E8A3', '#85E085', '#66D966',
              '#47D047', '#2ECF2E', '#1EBD1E', '#0DAB0D', '#009900'] if useGradientColor else None
    plt.pie(ages, labels=ages.index, autopct='%1.1f%%', colors=colors)
    plt.legend(loc='upper left', title="Age Group", title_fontsize=12)
    plt.tight_layout()

    return __plt2Bytes(plt)


def getGendersPiePlot() -> io.BytesIO:
    genders = __getDF().Gender.value_counts()
    plt.figure(figsize=(8, 8))
    plt.title("Genders")
    colors = [MCOLOR, FCOLOR]
    plt.pie(genders, labels=genders.index, autopct='%1.1f%%', colors=colors)
    plt.legend()

    return __plt2Bytes(plt)


def getAgeWithGenderPlot() -> io.BytesIO:
    df = __getDF()
    plt.figure(figsize=(10, 8))
    plt.title("Ages by Gender")
    sns.countplot(data=df, x="Age", hue="Gender", palette=[MCOLOR, FCOLOR])
    plt.ylabel("Count")

    return __plt2Bytes(plt)


def getAgeDistributionPlot() -> io.BytesIO:
    df = __getDF()
    plt.figure(figsize=(10, 8))
    plt.title("Ages Distribution")
    sns.histplot(data=df, x="Age", kde=True)

    return __plt2Bytes(plt)


def getCountByDateHist() -> io.BytesIO:
    df = __getDF()
    plt.figure(figsize=(10, 8))
    plt.title("Record Count by Date")
    sns.histplot(data=df, x="Datetime", bins=30)
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.xticks(rotation=90)
    plt.tight_layout()

    return __plt2Bytes(plt)


def getCountWithGenderByDateHist() -> io.BytesIO:
    df = __getDF()
    plt.figure(figsize=(10, 8))
    plt.title("Record Count with Gender by Date")
    sns.histplot(data=df, x="Datetime", hue="Gender",
                 palette=[MCOLOR, FCOLOR], bins=30, multiple="stack")
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.xticks(rotation=90)
    plt.tight_layout()

    return __plt2Bytes(plt)


def getCountWithAgeByDateHist() -> io.BytesIO:
    df = __getDF()
    plt.figure(figsize=(10, 8))
    plt.title("Record Count with Age by Date")
    sns.histplot(data=df, x="Datetime", hue="Age", bins=30, multiple="stack")
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.xticks(rotation=90)
    plt.tight_layout()

    return __plt2Bytes(plt)


if __name__ == "__main__":
    __display(getAgesPiePlot())
    # __display(getAgeWithGenderPlot())
    # __display(getCountByDateHist())
