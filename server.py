#!/usr/bin/python

import socket
import os
from threading import Thread
from subprocess import Popen

# globals

# initialize the song-to-votes dictionary
songdict = dict()

# maintain a list of new connections, ensuring we only make one thread per connection
new_connections = []

sock = socket.socket()
host = "192.168.43.104"
port = 12346

sock.bind((host, port))
sock.listen(5)

print "now listening!"

# find the highest voted song
def get_best_song():
    max_votes = -1
    best_song = ""
    for key, value in songdict.iteritems():
        curr_votes = value[1]
        if curr_votes > max_votes:
            max_votes = curr_votes
            best_song = value[0]
    print best_song + " " + str(max_votes)
    return (best_song, max_votes)


# initialize number of votes for each song to 0
def initialize_votes():
    counter = 1
    for song in os.listdir("songs"):
        songdict[counter] = [song, 0]
        counter += 1


def handle_initial_connection():
    while True:
        print "begin handle_initial_connection"
        connection, addr = sock.accept()
        print 'Got connection from', addr
        initial_message = "Thank you for connecting to this pi\n"
        initial_message += "Please vote for a song\n"
        counter = 1
        for song in os.listdir("songs"):
            initial_message += str(counter) + " " + song
            counter += 1
        connection.send(initial_message)

        thread = Thread(target=check_for_input, args=(connection,))
        thread.start()
        print "end handle_initial_connection"


# checks for user input, updates vote count based on song the user voted for
def check_for_input(connection):
    new_connections.remove(connection)
    vote = connection.recv(4096)
    print vote
    if vote.isdigit() and int(vote) <= len(songdict.keys()):
            print "valid vote"
            songdict[int(vote)][1] = songdict[int(vote)][1] + 1


def play_song(best_song):
    print "about to play song"
    os.system("omxplayer songs/" + best_song)
    print "finished playing song"

initialize_votes()

# create thread to handle new connections
thread = Thread(target=handle_initial_connection)
thread.start()
print "after thread"
while True:
    print "looping"
    # if song is not playing, play the most popular song
    if os.system("sh currently_playing.sh") != 0:
        best_song, max_votes = get_best_song()
        print "max votes: " + str(max_votes)
        thread = Thread(target=play_song, args=(best_song,))
        initialize_votes()

for connection in new_connections:
    connection.close()

sock.close()
