# evolveme

Track your movement/sport sessions and see how you evolve!

This app is built with [Reflex](https://github.com/reflex-dev/reflex)


To run the app, execute this command on the project root folder:


### Docker

More info on: [Reflex repo](https://github.com/reflex-dev/reflex)

```bash
# Download the image
docker build -t reflex-app:latest .
# Run a container
docker run -it --rm -p 3000:3000 -p 8000:8000 --name evolveme reflex-app:latest
```
