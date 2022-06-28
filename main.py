from flask import Flask
from flask import request
from flask import session
import jsonlines
import openai
openai.api_key = "YOUR KEY"

class Example():
    """Stores an input, output pair and formats it to prime the model."""

    def __init__(self, inp, out):
        self.input = inp
        self.output = out

    def get_input(self):
        """Returns the input of the example."""
        return self.input

    def get_output(self):
        """Returns the intended output of the example."""
        return self.output

    def format(self):
        """Formats the input, output pair."""
        return f"input: {self.input}\n {self.output}\n"

class GPT:
    """The main class for a user to interface with the OpenAI API.
    A user can add examples and set parameters of the API request."""

    def __init__(self, engine="text-davinci-002",
                 temperature=0.7,
                 max_tokens=256):
        self.examples = []
        self.engine = engine
        self.temperature = temperature
        self.max_tokens = max_tokens

    def add_example(self, ex):
        """Adds an example to the object. Example must be an instance
        of the Example class."""
        assert isinstance(ex, Example), "Please create an Example object."
        self.examples.append(ex.format())

    def get_prime_text(self):
        """Formats all examples to prime the model."""
        return '\n'.join(self.examples) + '\n'

    def get_engine(self):
        """Returns the engine specified for the API."""
        return self.engine

    def get_temperature(self):
        """Returns the temperature specified for the API."""
        return self.temperature

    def get_max_tokens(self):
        """Returns the max tokens specified for the API."""
        return self.max_tokens

    def craft_query(self, prompt):
        """Creates the query for the API request."""
        return self.get_prime_text() + "input: " + prompt + "\n"

    def submit_request(self, prompt):
        """Calls the OpenAI API with the specified parameters."""
        response = openai.Completion.create(
                                            model="text-davinci-002",
                                            prompt=self.craft_query(prompt),
                                            max_tokens=self.get_max_tokens(),
                                            temperature=0.3,
                                            top_p=1,
                                            n=1,
                                            stream=False,
                                            stop="\ninput:")
        return response

    def get_top_reply(self, prompt):
        """Obtains the best result as returned by the API."""
        response = self.submit_request(prompt)
        return response['choices'][0]['text']

gpt = GPT(engine="text-davinci-002",
          temperature=0.3,
          max_tokens=256)

gpt.add_example(Example('custom question', 
                        'custom answer'))

app = Flask(__name__)

@app.route("/")

def index():
    prompt = request.args.get("prompt", "")
    if prompt:
        answer = answer_from(prompt)
    else:
        answer=" "
    return (
        """<form action="" method="get">
                <input type="text" placeholder="Ask something" name="prompt" size="100">
                <input type="submit" name="submit" value="submit">
                <input type="reset" name="clear" value="clear">
            </form>"""
        + "Previous Question: "
        + prompt
        + " /// "
        + answer
    )

def answer_from(prompt):
    try:
        output = gpt.submit_request(prompt)
        print(output.choices[0].text)
        return (output.choices[0].text)
    except ValueError:
        return "Sorry, I don't know this one"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
