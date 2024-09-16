from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
import yaml

# New chatbot
chatbot = ChatBot(
    name='Misty',
    logic_adapters=[
        'chatterbot.logic.BestMatch',
        'chatterbot.logic.TimeLogicAdapter',
        'chatterbot.logic.MathematicalEvaluation',
    ]
)

# Train the bot with the English corpus
corpus_trainer = ChatterBotCorpusTrainer(chatbot)
corpus_trainer.train('chatterbot.corpus.english')

# Load custom weather YAML file
with open('weather_corpus.yml', 'r') as file:
    weather_data = yaml.safe_load(file)

# Extract conversations from the YAML file
conversations = weather_data.get('conversations', [])

# Flatten the list of conversations to a format suitable for ListTrainer
flattened_conversations = [item for sublist in conversations for item in sublist]

# Train the chatbot with custom weather conversations
list_trainer = ListTrainer(chatbot)
list_trainer.train(flattened_conversations)

print("Hello! How can I help you today?")
