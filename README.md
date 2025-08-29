# BBC English Podcast Scraper 🎧

A Scrapy-based project to automatically download **BBC English learning podcasts** (audio + transcripts), store them locally, and index them into a structured Excel file for easy study and review.

---

## 🌍 Motivation

During my years at university, I often had limited internet access.  
After my preliminary classes, I was eager to improve my English — with a strong focus on **British English**.  

The **BBC podcasts** became my main resource for self-study. They allowed me to learn at my own pace, combining listening practice (MP3s) with transcripts (PDFs).  

What started as two small scripts (`six_minutes_bbc_podcasts.py` and `utility_function.py`) has grown into something more ambitious.

Since the channel offers more excellent podcasts, I decided to build a more **robust and reusable scraping pipeline** using Scrapy.

At first, I wrote small scripts (`six_minutes_bbc_podcasts.py` and `utility_function.py`) to fetch the episodes I wanted so I could **study them offline at my own pace**.  

As my goals grew — and with the BBC releasing even more valuable podcasts — I wanted to make the process **more robust, automated, and reliable**. That’s how this Scrapy project was born.

---

## ✨ Features

- 📥 **Download podcasts & transcripts** directly from BBC sites  
- 📂 **Organize files** into folders by podcast and year  
- ⏭️ **Skip already-downloaded files** (with size checks)  
- 📊 **Track everything in Excel** (title, URLs, paths, release dates, etc.)  
- 📈 **Crawl statistics logged** at the end of each run  

---

## ⚙️ Installation

Clone the repository and install dependencies using [Pipenv](https://pipenv.pypa.io/):

```bash
git clone https://github.com/your-username/python_in_depth.git
cd python_in_depth

pipenv install --dev
```

---

## 🚀 Usage

Run the spider for a specified year's podcast.
Example:

```bash
scrapy crawl six_minutes_english -a years=2025
```

Run the spider for multiple year's podcast.
Example:

```bash
scrapy crawl six_minutes_english -a years=2025,2022,2015
```

Files are stored in:

```bash
~/Documents/BBC_English_Podcast/<PodcastName>/<Year>/
```

Excel summary is stored in:

```bash
~/Documents/BBC_English_Podcast/<PodcastName>/<PodcastName>.xlsx
```

---

## 📂 Output Example

### Folder Structure

```bash
BBC_English_Podcast/
└── Six_minutes_english/
    ├── 2023/
    │   ├── AI_in_everyday_life.pdf
    │   └── AI_in_everyday_life.mp3
    └── Six_minutes_english.xlsx
```

### Excel File Structure

| Title           | PDF URL                                                | PDF Path                                                    | MP3 URL                                      | MP3 Path                                                    | Page URL    | Release Date | Release Year | Status     |
| --------------- | ------------------------------------------------------ | ----------------------------------------------------------- | -------------------------------------------- | ----------------------------------------------------------- | ----------- | ------------ | ------------ | ---------- |
| Example Episode | [http://.../transcript.pdf](http://.../transcript.pdf) | /BBC\_English\_Podcast/Six_minutes_english/2025/Example\_Episode.pdf | [http://.../audio.mp3](http://.../audio.mp3) | /BBC\_English\_Podcast/Six_minutes_english/2025/Example\_Episode.mp3 | http\://... | 2025-08-29   | 2025         | Downloaded |

---

## 📈 Crawl Summary

After each run, the following statistics are logged:

- 🌐 Total requests sent
- 📌 Episodes scheduled
- ✅ Episodes fetched (HTTP 200)
- 📝 Total Excel rows
- 📄 PDFs downloaded
- ⏭️ PDFs skipped (already exist)
- 🎵 MP3s downloaded
- ⏭️ MP3s skipped (already exist)

## 📜 License  

This project is licensed under the **MIT License** – feel free to use, learn from, or build upon it.  
