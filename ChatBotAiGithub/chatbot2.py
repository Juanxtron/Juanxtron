

import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import BertTokenizerFast, BertForQuestionAnswering, Trainer, TrainingArguments, pipeline
from dash import Dash, html, dcc, Input, Output, State
from datasets import load_dataset

# Paso 1: Cargar y limpiar datos
df = pd.read_csv("C:/Users/jpcan/OneDrive/Documentos/Andes Universidad/Analitica computacional/Github portafolio/Chatbot/Cleaned_Salud_Sexual_Preguntas.csv", on_bad_lines='skip')
df.rename(columns={df.columns[1]: 'respuesta'}, inplace=True)
df['respuesta'] = df['respuesta'].str.replace(';;;;', '').str.strip()

# Asegurarnos de que todas las preguntas y respuestas sean cadenas de texto
df['pregunta'] = df['pregunta'].astype(str)
df['respuesta'] = df['respuesta'].astype(str)

# Crear un contexto artificial
contexto = "Información sobre salud sexual."

# Verificar las columnas
print(df.head())
print(df.columns)

# Paso 2: Tokenización de los datos
tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')

def add_token_positions(encodings, answers, tokenizer):
    start_positions = []
    end_positions = []

    for i in range(len(answers['input_ids'])):
        answer_ids = answers['input_ids'][i][1:-1]  # Exclude [CLS] and [SEP]
        encoding_ids = encodings['input_ids'][i]
        start_idx = (encoding_ids == answer_ids[0]).nonzero(as_tuple=True)[0]
        end_idx = (encoding_ids == answer_ids[-1]).nonzero(as_tuple=True)[0]

        if len(start_idx) > 0 and len(end_idx) > 0:
            start_positions.append(start_idx[0].item())
            end_positions.append(end_idx[0].item())
        else:
            start_positions.append(0)
            end_positions.append(0)

    return start_positions, end_positions

# Tokenizar preguntas y contexto artificial
questions_encodings = tokenizer(df['pregunta'].tolist(), truncation=True, padding=True, return_tensors="pt")
context_encodings = tokenizer([contexto] * len(df), truncation=True, padding=True, return_tensors="pt")

# Combinar preguntas y contexto en una sola secuencia
inputs = tokenizer(df['pregunta'].tolist(), [contexto] * len(df), truncation=True, padding=True, return_tensors="pt")
answers_encodings = tokenizer(df['respuesta'].tolist(), truncation=True, padding=True, return_tensors="pt")

# Agregar posiciones de inicio y fin de las respuestas
start_positions, end_positions = add_token_positions(inputs, answers_encodings, tokenizer)

class QADataset(Dataset):
    def __init__(self, encodings, start_positions, end_positions):
        self.encodings = encodings
        self.start_positions = start_positions
        self.end_positions = end_positions

    def __getitem__(self, idx):
        item = {key: val[idx].clone().detach() for key, val in self.encodings.items()}
        item['start_positions'] = torch.tensor(self.start_positions[idx])
        item['end_positions'] = torch.tensor(self.end_positions[idx])
        return item

    def __len__(self):
        return len(self.start_positions)

# Preparar el dataset
dataset = QADataset(inputs, start_positions, end_positions)

# Paso 3: Configuración del modelo
model = BertForQuestionAnswering.from_pretrained('bert-base-uncased')

# Paso 4: Preparar el dataset para entrenamiento
train_dataset = dataset

# Paso 5: Configurar los argumentos de entrenamiento
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=2,  # Reducir el número de épocas
    per_device_train_batch_size=8,  # Aumentar el tamaño del lote
    per_device_eval_batch_size=8,  # Aumentar el tamaño del lote
    warmup_steps=100,
    weight_decay=0.01,
    logging_dir='./logs',
)

# Paso 6: Entrenar el modelo con el dataset
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=train_dataset  
)

trainer.train()

# Paso 7: Evaluar el modelo
evaluation = trainer.evaluate()
print(f"Evaluation results with custom dataset: {evaluation}")

# Paso 8: Guardar el modelo entrenado
model.save_pretrained('./trained_model_custom')
tokenizer.save_pretrained('./trained_model_custom')

# Paso 9: Descargar el dataset SQuAD-es (SQuAD en español)
# Usar solo el 5% del conjunto de datos para un entrenamiento más rápido y especificar la configuración
squad_es = load_dataset('squad_es', 'v1.1.0', split='train[:1%]')

# Paso 10: Preparar el dataset SQuAD-es
def prepare_features(examples):
    questions = [q.strip() for q in examples["question"]]
    inputs = tokenizer(
        questions,
        examples["context"],
        max_length=256,  # Reducir el tamaño máximo de secuencia
        truncation="only_second",
        return_offsets_mapping=True,
        padding="max_length",
    )

    offset_mapping = inputs.pop("offset_mapping")
    answers = examples["answers"]
    start_positions = []
    end_positions = []

    for i, offsets in enumerate(offset_mapping):
        answer = answers[i]
        start_char = answer["answer_start"][0]
        end_char = start_char + len(answer["text"][0])

        sequence_ids = inputs.sequence_ids(i)

        context_start = sequence_ids.index(1)
        context_end = len(sequence_ids) - 1 - sequence_ids[::-1].index(1)

        if not (offsets[context_start][0] <= start_char and offsets[context_end][1] >= end_char):
            start_positions.append(0)
            end_positions.append(0)
        else:
            start_idx = next(idx for idx, offset in enumerate(offsets) if offset[0] <= start_char and offset[1] > start_char)
            end_idx = next(idx for idx, offset in enumerate(offsets) if offset[0] < end_char and offset[1] >= end_char)

            start_positions.append(start_idx)
            end_positions.append(end_idx)

    inputs["start_positions"] = start_positions
    inputs["end_positions"] = end_positions
    return inputs

tokenized_squad_es = squad_es.map(prepare_features, batched=True, remove_columns=squad_es.column_names)

# Paso 11: Entrenar el modelo con el dataset SQuAD-es
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_squad_es,
    eval_dataset=tokenized_squad_es 
)

trainer.train()

# Paso 12: Evaluar el modelo entrenado con SQuAD-es
evaluation_squad_es = trainer.evaluate()
print(f"Evaluation results with SQuAD-es dataset: {evaluation_squad_es}")

# Paso 13: Guardar el modelo entrenado con SQuAD-es
model.save_pretrained('./trained_model_squad_es')
tokenizer.save_pretrained('./trained_model_squad_es')

# Paso 14: Cargar el modelo entrenado y usarlo en una aplicación
nlp = pipeline("question-answering", model='./trained_model_squad_es', tokenizer='./trained_model_squad_es')

def responder_pregunta(pregunta):
    context = "Información sobre salud sexual."
    result = nlp(question=pregunta, context=context)
    return result['answer']

# Paso 15: Integrar el modelo con Dash
app = Dash(__name__)

app.layout = html.Div(
    style={
        'background-image': 'url("/assets/fondo.jpg")',  # Ruta ajustada para usar la imagen desde la carpeta assets
        'background-size': 'cover',
        'height': '100vh',
        'display': 'flex',
        'justify-content': 'center',
        'align-items': 'center',
        'flex-direction': 'column',
        'color': 'black',  # Cambiar el color a negro
        'text-align': 'center',
        'padding': '20px'
    },
    children=[
        html.H1("Información sobre Educación Sexual en Colombia", style={'font-size': '3em', 'margin-bottom': '20px', 'color': 'black'}),  # Cambiar el color a negro
        dcc.Input(id="input-pregunta", type="text", placeholder="Escribe tu pregunta aquí", style={'width': '80%', 'padding': '10px', 'font-size': '1.5em', 'margin-bottom': '20px'}),
        html.Button('Enviar', id='submit-button', n_clicks=0, style={'padding': '10px 20px', 'font-size': '1.5em', 'cursor': 'pointer'}),
        html.Div(id="output-respuesta", style={'margin-top': '20px', 'font-size': '1.5em', 'color': 'black'})  # Cambiar el color a negro
    ]
)

@app.callback(
    Output("output-respuesta", "children"),
    [Input("submit-button", "n_clicks")],
    [State("input-pregunta", "value")]
)
def update_output(n_clicks, pregunta):
    if n_clicks > 0 and pregunta:
        respuesta = responder_pregunta(pregunta)
        return f"Respuesta: {respuesta}"
    return ""

if __name__ == '__main__':
    app.run_server(debug=True)
