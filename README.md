# Union-Info-Vis-Project


List of Unions spreadsheet: https://docs.google.com/spreadsheets/d/1JQmKm9AMQQ_dfXc-oJeXsESaFfi3ZKCVUGivgnWx7Ro/edit?usp=sharing

## Running the Code
Visualization is a Dash web app, but currently just on localhost:8050 and not on an actual site.

IF RUNNING FOR THE FIRST TIME: 
1. Run pdf_to_png.py first to generate individual images fromt the background contract PDF
2. Run the app.py file and open http://localhost:8050/ in your web browser
See requirements.txt for required libraries that may need to be installed.

## Final Project Requirements:
- [x] Must contain a form of color encoding
- [x] Must include brushing and linking
- [x] Must include overview concept
- [x] must include details-on-demand
- [x] must include two different visual encodings

## DEADLINES
- [ ] 12/9 1:35pm presentation, demo video
- [ ] 12/10 5:pm paper

## Last Minute To-Do
- [ ] Bigger titles and subtitles A
- [ ] Fix timeline vis N
    - [ ] Comparing changes?
    - [ ] Explaining what "no change" means OR filter out with regex
    - [ ] Drop bar chart, add another column to table to show previous changes
    - [ ] On main timeline, opacity = # changes?
- [ ] Update stipend visualizations A
    - [ ] Make the living wage/poverty line pop out more
    - [ ] Vertical line was confusing?
- [ ] Benefits A
    - [ ] Unique emojis
    - [ ] Legend at bottom of what emojis are
    - [ ] Include corresponding emoji in title of bar chart
- [ ] Write instructions for use at top N
- [ ] Table of contents at top/links to diff vis boxes A
- [ ] More explanations for vis/longer captions (e.g. explain groupings in timeline) N
- [ ] Titles on boxes A
- [ ] Write paper AN
- [ ] Create demo (Alenna) 
- [ ] Write presentation/slide deck ANNNNN
- [ ] IF TIME: Tutorial for visualizations A
- [ ] IF TIME: Highlight on hover (if pink, it's clickable) A
- [ ] IF NO TIME: Specialized instructions on each modal for what you can click N

## Tasks:
- [ ] Miscellaneous/post-user feedback tasks
    - [ ] Add arrows to timeline for clarity N
    - [ ] Label clickable boxes A
    - [x] Dynamic box configuration 
    - [ ] Add instructions on how to navigate to the more complicated vis N
    - [ ] More visualizations? AN
    - [ ] Write paper AN
    - [ ] Do demo A
    - [ ] Do presentation N
    - [ ] Desaturated background on all charts N
    - [ ] Deliberate abt color scheme AN

- [ ] Dashboard set up
    - [x] Contract loaded as background 
    - [x] Pop-ups working, showing visualization
    - [x] Pop-ups linked to correct spots in pdf
- [ ] Boston area university stipends
    - [ ] Title 
    - [ ] Subtitle 
    - [x] Legend 
    - [ ] Color scheme 
        - [ ] Make neu red and neutral others
    - [ ] Annotations (ex: extra dotted lines, arrows)
        - [ ] Make the line annotations just for 2024-25
        - [ ] Add note about self reported data and reliability and avgs over time
        - [ ] make the living wage a standout color
    - [ ] Background N
    - [ ] Axis labels
        - [ ] y axis labels should be k
        - [ ] x axis show ticks for every year
    - [ ] Tooltips
        - add year annotation on tooltip
    - [x] Data selection
- [ ] Stipends by Department over Time
    - [ ] Title
    - [ ] Subtitle
    - [ ] Legend
        - [ ] Capitalize legend
    - [ ] Color scheme
        - [ ] choose better plotly color scheme
    - [ ] Annotations (ex: extra dotted lines, arrows)
        - [ ] Add living wage and poverty lines
    - [ ] Background N
    - [ ] Axis labels
        - [ ] Make it K
        - [ ] all years for x axis ticks
    - [ ] Tooltips
        - [ ] add year: year
    - [x] Data selection
    - [ ] [WISHLIST] add option to filter by department vs college
    - [ ] [WISHLIST] add violin-plot style tubes on departments self report
- [ ] benefits contract comparison
    - [ ] Title
    - [ ] Subtitle
    - [ ] Legend
        - [ ] Add legend showing what icon matches what benefit
    - [ ] Color scheme
        - [ ] Change red/green to blue/yellow bc red is NEU
    - [ ] Labels
        - [ ] Unique icons
        - [ ] add icon to table title
        - [ ] fix positions of schools on side table
    - [x] Annotations (ex: extra dotted lines, arrows)
    - [ ] Background 
        - [ ] remove white line grid
    - [x] Axis labels
    - [ ] Tooltips
        - [ ] on-hover show explanation of what a benefit means
    - [ ] Data selection
        - [ ] Filter by network buttons
- [ ] Timeline
    - [ ] Title
    - [ ] Subtitle
        - [ ] in instructions, make it obvious what you can click
        - [ ] subtitle with instructions on subplot
    - [x] Legend
    - [ ] Color scheme
        - [ ] union as red(?)
    - [ ] Labels
        - [ ] Labels are cut off 
    - [ ] Annotations (ex: extra dotted lines, arrows)
    - [ ] Background
    - [x] Axis labels
    - [ ] Axes 
        - [ ] In the subtable, add current and end changes
    - [ ] Tooltips
        - [ ] Add duration until next change
        - [ ] Per topic explanation tooltip stating what something is A
    - [ ] Dropdown to choose between topics
        - [ ] Add explanation of groupings
        - [ ] For 3 employment groups, give explanation and theme
    - [ ] Wrap topic titles
    - [ ] Arrow to either axis or bars
    - [ ] Add explicit scrollbar to the table or subtitle explaining it
    - [ ] Add text explanation of "no change"
    - [ ] Sub-table 
        - [ ] add second column for "final"
- [ ] [WISHLIST] Comparison of visa benefits 

