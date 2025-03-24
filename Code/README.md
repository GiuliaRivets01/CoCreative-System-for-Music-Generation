### MUSIC GENRES
Instead of asking the users to specify music parameters (like the number of notes, the number of bars, ...)
I've asked the user to specify just the genre and then based on the music genre the program
automatically chooses the parameters.
I've decided to choose 4 genres: rock, house, Vivaldi and Mozart.
Vivaldi represents Violin music whereas Mozart represents piano music.
I thought it was a little bit more interesting to put "Vivaldi" and "Mozart" as two music genres.
Each genre is characterized by a series of parameters defined in "GENRE_PARAMETERS" dictionary.

### PAUSES
Another thing I've modified in the code is the usage of pauses. I thought that too many
pauses were inserted with the original version of the code, so for the genres that actually have
pauses, I've decided to follow this rule: a note is a pause if by randomly drawing a number between
0 and 1, the number is less or equal to 0.2

### ACTUAL MUSIC
In order to make the music a little bit better (which is also what the guy on Youtube did), I've used
an online tool to process the music and make it more similar to its genre. I didn't use the same
website that the guy on Youtube used because it costs, but I used 'soundtrap' which is free.
In particular, I've used the following instruments provided by that website:
- for rock music: *Guitar - Rock - Warm Lead*
- for house music: *Synths - Rythmic - The Best*
- for Vivali (violin) music: *Orchestral - String Ensemble - Studio Quartet Spiccato*
- for Mozart (piano) music: *Keys - Pianos - Grand piano*

You can find the final version (processed using soundtrap) in the songs folder.
I've only run the code for a population of 2, so the songs probably can be better,
but it was just to give have an idea of how they turn out.