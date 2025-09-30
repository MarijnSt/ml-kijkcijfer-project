# Kijkcijfer Project
This project was part of the AI & Data Engineer micro-credential that I'm doing this year at HOGENT. It's the main project for the Machine Learning course in the first semester.

The objective is pretty simple: build a regression model that can predict ratings for TV shows in Flanders.

There is public data available thanks to CIM (Centrum voor Informatie over Media). They publish a top 20 of most-watched Flemish TV shows each day.

In addition to the CIM data, we were allowed to use any other open data sources
I decided to factor in some weather data as I believe it's a big influence on whether people stay in and watch TV or go out and enjoy the weather. This data is available through the open-meteo API. 

## Project Refactoring
I'm currently working on refactoring this project based on feedback I got during my exam and based on things I've picked up the last couple of months working on other projects.

Restructuring the project was quite high on my to-do list as I want it to more closely resemble an ETL project. I've separated notebooks, logs, data and exam files into separate folders, but most of the project's functionality is now in the src folder.

Before this refactoring, all the code was in one notebook. You can see how that looked in the v1 folder where I kept all my original files that I submitted for my exam.

It is nice to have all the code in one notebook and add some text to clarify my thinking and experimentation with the data, but it's not very future-proof that way. Something I really liked when I was working as a Full Stack developer is an organized repository with clear separation of concerns and code that can be tested.

Web projects are organized differently, so I took inspiration from ETL projects I found online and with the help of my AI assistant.

I still kept some notebooks to experiment with the data, but all the functionality of extracting, transforming and loading the data has been moved to the src folder.
Another big advantage of working with separate Python modules is that Git works a lot better. 

Git differential files for notebooks are a nightmare to read. I don't want to think about having to do code reviews that way. With these separate modules, it's a lot easier to collaborate on projects like this. I'm working on this one alone, but I see it as a good way to practice for future projects.