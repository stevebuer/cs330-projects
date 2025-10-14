# CS330 Homework 2 Project Development

My goal in this iteration is to move the project from a proof-of-concept/prototype stage to a pre-alpha working system deployed into a production environment.

## Initial list of features for this iteration

These are the list of features or goals that I have considered for implementing. I will preserve this to-do list here and then document the work in a section below.
Anything remaining will need to be pushed to the next iteration or re-factored.

* Configure DNS with server name: dx.jxqz.org
* Configure Apache Web Server to support this virtual host.
* Install Postgres server into production environment and configure users and access control.
* Migrate (or create) database schema for Postgres.
* Rewrite the dx cluster scraping program to have:
   * Fault tolerance and error handling
   * Stop, Start, Status Control interface for the web API to hook to
   * Logging of status error conditions to syslog or similar
   * Options for: raw storage of data to text file or database insert
   * Packaging and Deployment mechanism
* Initial pass of a Web UI control panel in the style of a monitoring dashboard (for now)
* Updated Schema Documentaion
* Chat Logs and the Usual
* SQL quick reference and study guide
* Consider a deployment strategy: packages, containers, etc?
* CI/CD pipline and automated testing?

## Development Tasks

### DNS Configuration

A CNAME record for dx.jxqz.org was added to my DNS configuration in my [domain registrar](www.porkbun.) portal.

### Configure Apache virtual server

I have an existing Linux virtual machine that runs my website. I [asked Copilot](chat-transcripts/apache2-chat.md) to create
an [Apache2](https://httpd.apache.org/docs/2.4) config file [dx.jxqz.org.conf](config/dx.jxqz.org.conf) to create another virtual 
server for this project. I followed the instructions listed in the [chat transcript](chat-transcripts/apache2-chat.md) to manually
install the file and restart the server. Tested. The site dx.jxqz.org loads successfully with an empty directory listing.

### Postgresql production install and config

Used *sudo apt install postgresql* to install postgres on the production server.

I [asked Copilot](chat-transcripts/db-roles.md) to help me move the postgres version of my scripts to the curreny directory and create roles for the various programs that will connect to the RDBMS server.

### Initial Web UI Creation

I chatted with copilot and asked about the best UI frameworks for data science type projects.

---

**Given your preferences—Python-based, no notebooks, real-time data, and predictive AI models—here are the top UI frameworks that best suit your needs:**

### ⚡ Best Python UI Frameworks for Real-Time AI Dashboards

| Framework     | Strengths for Your Use Case                                      | Ideal For                                      |
|---------------|------------------------------------------------------------------|------------------------------------------------|
| **Dash**      | Highly customizable, supports real-time updates, integrates well with Plotly and Flask | Production-grade dashboards with complex UI    |
| **Streamlit** | Fast prototyping, simple syntax, supports real-time widgets and model outputs | Lightweight apps and quick deployment          |
| **Panel**     | Flexible layout, supports multiple plotting libraries, good for streaming data | Multi-visual dashboards with PyData stack      |
| **Reflex**    | React-powered Python framework, great for dynamic UIs and state management | Modern, reactive apps with real-time interactivity |
| **Gradio**    | Ideal for ML model demos, supports live inputs and outputs       | Sharing AI models with interactive interfaces  |

### 🧠 Recommendation Based on Your Needs
- **For real-time predictive AI models**: **Dash** and **Reflex** offer the most control and scalability. Dash is mature and enterprise-ready, while Reflex is newer but React-powered for dynamic UIs.
- **For simplicity and speed**: **Streamlit** is excellent if you want to get up and running quickly with minimal code.
- **For multi-library support**: **Panel** is great if you're using tools like Bokeh, Matplotlib, or Holoviews.

Would you like help scaffolding a starter dashboard with one of these frameworks?

---

Based on these recommendations I [asked Claude Sonnet 3.5](chat-transcripts/web-ui-transcript.md) to create me a basic web application framework. I then
went about installing the dependencies and attempting to get the system up and running in the "production environment" and on my laptop in some for as well
for testing and further development.

I started with the testing environment. I have not previously worked with [Python WSGI](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) so I will need to read up on it. However,
I have used CGI and mod_python previously for extremely simple tasks.

I modfied the apache2 config file to use an alternate name for the test/dev server: dxdev.jxqz.org. I created an entry in my local /etc/hosts file for this hostname resolving to 127.0.0.5.

*sudo a2ensite dxdev.jxqz.org ; sudo systemctl reload apache2*

#### WSGI and Pyton Dependencies

I need install dependencies in my development virtual environment. Looks like the updated [apache2 config for WSGI](config/dx.jxqz.org.conf)
will attempt to run out of my venv and git repositing which is fine for now. 

```
source ~/cs330_venv/bin/activate
```

Now I can install my [python dependencies](requirements-web.txt).

```
pip install -r requirements-web.txt
```

Result: lots of packages downloaded and installed successfully.

First attempt to start the server and web app was not successful. Getting permissions errors. Had to do some manual edits on apache config like setting venv path.

Update: After hacking on this for about an hour and a half [it is clear](docs/wsgi-error.txt) that the AI generated Apache2 config and instructions are not going to be enough to get this
running. I am going to have to dig into the Python [mod_wsgi documentation](https://www.modwsgi.org/en/develop/user-guides/virtual-environments.html). Hopefully, I 
will only have to do this once and then my development and production environments will be set up for the remainder of the project. 

**Apache / mod_wsgi setup steps**

1. Install apache2, libapache2-mod-wsgi-py3 dpkg
2. Create venv that will be used by the python wsgi instance for this application
3. Create a DocumentRoot for the application
4. Create an apache site configuration file for the virtual host
5. Check directory ownership, permissions, and other gotchas
6. Enjoy your new application
