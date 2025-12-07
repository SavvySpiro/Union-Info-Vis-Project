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
- [x] Bigger titles and subtitles A
- [ ] Fix timeline vis N
    - [x] Comparing changes?
    - [ ] Explaining what "no change" means OR filter out with regex
    - [x] Drop bar chart, add another column to table to show previous changes
    - [x] On main timeline, opacity = # changes?
- [ ] Update stipend visualizations A
    - [x] Make the living wage/poverty line pop out more
    - [x] Vertical line was confusing?
- [x] Benefits A
    - [x] Unique emojis
    - [x] Legend at bottom of what emojis are
    - [x] Include corresponding emoji in title of bar chart
- [ ] Write instructions for use at top N
- [x] Table of contents at top/links to diff vis boxes A
- [ ] More explanations for vis/longer captions (e.g. explain groupings in timeline) N
- [x] Titles on boxes A
- [ ] Write paper AN
- [ ] Create demo (Alenna) 
- [ ] Write presentation/slide deck ANNNNN
- [ ] IF TIME: Tutorial for visualizations A
- [ ] IF TIME: Highlight on hover (if pink, it's clickable) A
- [ ] IF NO TIME: Specialized instructions on each modal for what you can click N

## Tasks:
- [ ] Miscellaneous/post-user feedback tasks
    - [x] Add arrows to timeline for clarity N
    - [x] Label clickable boxes A
    - [x] Dynamic box configuration 
    - [ ] Add instructions on how to navigate to the more complicated vis N
    - [ ] More visualizations? AN
    - [ ] Write paper AN
    - [ ] Do demo A
    - [ ] Do presentation N
    - [x] Desaturated background on all charts N
    - [x] Deliberate abt color scheme AN

- [x] Dashboard set up
    - [x] Title and subtitle for whole project
    - [x] Contract loaded as background 
    - [x] Pop-ups working, showing visualization
    - [x] Pop-ups linked to correct spots in pdf
- [x] Boston area university stipends
    - [x] Title 
    - [x] Subtitle 
    - [x] Legend 
    - [x] Color scheme 
        - [x] Make neu red and neutral others
    - [x] Annotations (ex: extra dotted lines, arrows)
        - [x] Make the line annotations just for 2024-25
        - [x] Add note about self reported data and reliability and avgs over time
        - [x] make the living wage a standout color
    - [x] Background N
    - [x] Axis labels
        - [x] y axis labels should be k
        - [x] x axis show ticks for every year
    - [x] Tooltips
        - [x] add year annotation on tooltip
    - [x] Data selection
- [x] Stipends by Department over Time
    - [x] Title
    - [x] Subtitle
    - [x] Legend
        - [x] Capitalize legend
    - [x] Color scheme
        - [x] choose better plotly color scheme
    - [x] Annotations (ex: extra dotted lines, arrows)
        - [x] Add living wage and poverty lines
    - [x] Background 
    - [x] Axis labels
        - [x] Make it K
        - [x] all years for x axis ticks
    - [x] Tooltips
        - [x] add year: year
    - [x] Data selection
    - [x] [WISHLIST] add option to filter by department vs college
    - [ ] [WISHLIST] add violin-plot style tubes on departments self report
- [x] benefits contract comparison
    - [x] Title
    - [x] Subtitle
    - [x] Legend
        - [x] Add legend showing what icon matches what benefit
    - [x] Color scheme
        - [x] Change red/green to blue/yellow bc red is NEU
    - [x] Labels
        - [x] Unique icons
        - [x] add icon to table title
        - [x] fix positions of schools on side table
    - [x] Annotations (ex: extra dotted lines, arrows)
    - [x] Background 
        - [x] remove white line grid
    - [x] Axis labels
    - [x] Tooltips
        - [x] on-hover show explanation of what a benefit means
    - [x] Data selection
        - [x] Filter by network buttons
- [ ] Timeline
    - [x] Title
    - [x] Subtitle
        - [x] in instructions, make it obvious what you can click
        - [x] subtitle with instructions on subplot
    - [x] Legend
    - [x] Color scheme
        - [x] union as red(?) (rejected; red for NEU, blue for union, green for agreement)
    - [x] Labels
        - [x] Labels are cut off 
    - [x] Annotations (ex: extra dotted lines, arrows)
    - [x] Background
    - [x] Axis labels
    - [x] Axes 
        - [x] In the subtable, add current and end changes
    - [ ] Tooltips
        - [x] Add duration until next change
        - [ ] Per topic explanation tooltip stating what something is A
    - [ ] Dropdown to choose between topics
        - [ ] Add explanation of groupings
    - [x] Wrap topic titles
    - [x] Arrow to either axis or bars
    - [x] Add explicit scrollbar to the table or subtitle explaining it
    - [ ] Add text explanation of "no change"
    - [x] Sub-table 
        - [x] add second column for "final"
- [ ] [WISHLIST] Comparison of visa benefits 

