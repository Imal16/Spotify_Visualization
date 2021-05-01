# Spotify_Visualization
## About

The project is a Python client to Spotify's Web API which is based on REST Principles.
There is the option to obtain User data, however it requires the user to Authenticate. In addition, to use the code, you need to register an application in Spotify's Dev website in order to obtain an Secret Key and Client Id to use their Web API.

Currently, within the code there is already data stored to generate a network of Top Artists and their related Artists. There is functions within the code to allow generation of a network from User data.

Sample network graph found at example.html

### Requirements/ Packages Used

Requests, Urlencode, secrets, Flask, Pyvis, Networkx, Jupyter notebook.

### Opportunities to improve the project

- Create a better way classify Artists in genres for the grouping and coloring of the network.
- Create Generalized sound profiles between artist to identify what is the most discriminating factor between them and color the network's edges appropriately. Ex: Artist A's music is more danceable than Artist B, so that edge should be labeled as such.

#### Note
- Basic API client was followed from a tutorial by Coding For Entrepreneurs to obtain good structure and format for coding an API Client (Covered basic search and application Auth).
- Additional Client features was coded myself such as understanding and functioning of User Authorization and obtaining User Data. Idea of building a network of Artist was also mine)
