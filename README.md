# Chat

#### Project 1 from UC Berkeley's CS 168 (Introduction to the Internet: Architecture and Protocols)

A simple application that connects users over a network: a chat server. Similar to chat programs like Slack and IRC, the finished chat server will allow users to converse in different channels. Users can create and join channels; once a user is in a particular channel, all messages that she sends will be relayed to all other users in that channel.

Server Usage:
    python2 server.py server_port

Client Usage:
    python2 client.py client_name server_address server_port
    
    Control message:
      /list    List all current chat channels
      /create  Create a channel
      /join    Join an existing channel
