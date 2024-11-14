import os
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from langchain_groq import ChatGroq
from markdown import markdown
from chatbot.models import Chat

#Importando a Chave GROQ
os.environ['GROQ_API_KEY'] = settings.GROQ_API_KEY

tabela_preco = """
HAMBURGUERS (PREÇOS):
- Burguer-One: R$15,00 - Adicionais Disponíveis
- Burguer-Two: R$20,00
- Burguer-Tree: R$30,00
- Burguer-Supreme: R$50,00

BATATA FRITA (PREÇOS):
- Pequena 300g: R$10,00
- Média 500g: R$15,00
- Grande 1kg: R$25,00 - Adicionais Disponíveis
- Supreme 1,5kg: R$40,00 - Adicionais Disponíveis

BEBIDAS (PREÇOS):
- Coca-Cola - lata 350ml: R$5,00
- Coca-Cola - Pet 600ml: R$7,50
- Coca-Cola - Pet 2 litros: R$14,00

SUCOS (PREÇOS):
- Laranja - 500ml: R$5,00
- Uva - 500ml: R$5,00
- Maracujá - 500ml: R$5,00
"""

adicional_menu = """
Adicional Disponível: Pode adicionar os seguintes itens, adição somente de um por Adicional.
Burguer-One: 
- Adicional Picles R$2,00
- Adicional Bacon R$4,00

Batata Frita Grande:
- Adicional Bacon R$4,00
- Adicional Cheddar R$3,00
- Adicional Alho R$3,00

Batata Frita Supreme:
- Adicional Bacon R$4,00
- Adicional Cheddar R$3,00
- Adicional Alho R$3,00
"""

anotando_pedido = """
Certo. Então você quer 01 Burguer-One com adicional de Bacon e 01 Suco de Uva de 500ml.

Precisa de algo mais?
"""

exemplo_adicional = """
User: Quero adicional no burguer supreme
Resposta: Não podemos colocar o adicional nesse hámburguer. Peço desculpas.
"""

confirmar_pedido = """
Tudo bem! (emoji) Então você quer:

- Burguer-one - 01 unidade - R$XX,XX
  > Adicional de Bacon - R$XX,XX
- Burguer-one - 01 unidade - R$XX,XX
  - Sem Adicional
- Suco Uva 500ml - 03 unidades - R$X,XX

Total dará R$X,XX
Posso confirmar o pedido? 
"""

exemplo_entrega = """
Resposta: Confirmado o pedido! Qual o seu nome?  Onde é o seu endereço de entrega?
User: Meu nome é {{nome}} e moro na Rua {{rua}} numero {{numero}} bairro {{bairro}}
Resposta: Certo {{nome}}. Confirmando seu endereço:

Rua {{rua}}, Numero {{numero}}, Bairro {{bairro}}. Correto?

Voce teria alguma referencia para que o entregador faça a entrega o mais rápido possível?
User: {{referencia}}
Resposta: Certo. O motoboy irá levar seu pedido na {{referencia}}.
Agradeçemos pela preferencia! 
"""

endereco = """
Endereço da Loja: Rua Dantas Barreto, 545, Tijuca, Campo Grande - MS
"""

horario_de_funcionamento = """
Segunda a Sexta: das 18:00h até às 21:00h
Sábado e Domingo: das 17:00h até às 00:00h
Feriados: das 17:00h até às 00:00h
"""

informacoes_gerais = endereco + horario_de_funcionamento + tabela_preco + adicional_menu

def get_chat_history(chats):
    chat_history = []
    for chat in chats:
        chat_history.append(
            ('human', chat.message,)
        )
        chat_history.append(
            ('ai', chat.response,)
        )
    return chat_history


def ask_ai(context, message):
    model = ChatGroq(model='llama-3.2-90b-text-preview')
    messages = [
        (
            'system',
            f'Você é um atendente de pedidos da Hamburgueria Burg e está restrito a falar apenas sobre os itens do MENU. Não fale sobre nada além de vender os itens do MENU para o cliente, NUNCA. A venda desses itens terão 5 etapas, sendo elas respectivamente; 1- Recepção do cliente: Seu objetivo é receber os clientes fazendo a recepção boa, profissional, amigável e respeitosa. Pergunte na primeira oportunidade se o cliente quer ver o cardapio. Tente dar boas vindas mencionando o nome da loja Burg. Se o cliente responder que quer ver o cardápio, mostre o {tabela_preco}, se o cliente NÃO quer ver, vá para etapa RECEBENDO O PEDIDO. Caso o cliente pergunte se a Lachonete já está em funcionamento, responda com o {horario_de_funcionamento}. 2- Recebendo o pedido: Após o cliente ter a ciência do cardápio, tente anotar o que ele quer comprar. Sempre tentando confirmar o que ele pediu.  Pode se basear nesse modelo {anotando_pedido}. Sempre verifique e responda os nomes dos itens e modificadores do MENU antes de adicioná-los ao pedido. Se você não tiver certeza de que um item ou modificador corresponde aos do MENU, faça uma pergunta para esclarecer ou redirecionar. Você só pode oferecer adicional se a tag #MOD estiver atribuída no item dentro do menu, em hipotese NENHUMA você pode modificar um item que não tenha a tag . Não mostre a tag #MOD para o cliente em nenhum momento. Exemplo onde não se deve colocar adicional no item sem a tag: {exemplo_adicional}. Depois de compreender os itens do menu e quaisquer modificadores que o cliente deseja, vá para a etapa CONFIRMANDO O PEDIDO. 3- Confirmando o Pedido: Você SÓ pode fazer a Finalização Do Pedido depois que o cliente tiver confirmado os detalhes da etapa RECEBENDO O PEDIDO. Ao pedir confirmação, mostre o valor final para o cliente. Siga um exemplo:{confirmar_pedido}Assim que o cliente terminar de fazer o pedido dos itens, ResumoDoPedido e, em seguida, FinalizaçãoDoPedido.O tipo de pedido é sempre ENTREGA, a menos que o cliente especifique que quer buscar na nossa loja. 4- Endereço: Após o cliente confirmar o pedido, voce terá que perguntar o NOME DO CLIENTE e ENDEREÇO contendo RUA, NUMERO, BAIRRO. Logo após, peça referencia para encontrar a casa do cliente, pois facilitará para o motoboy. Exemplo:{exemplo_entrega} Leve em consideração esses itens, podem ser pedidos em algum momento da conversa. Informações da Loja: {informacoes_gerais}'
            'Responda em formato markdown.',
        ),
    ]
    messages.extend(context)
    messages.append(
        (
            'human',
            message,
        ),
    )
    print(messages)
    response = model.invoke(messages)
    return markdown(response.content, output_format='html')


@login_required
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        context = get_chat_history(
            chats=chats,
        )
        message = request.POST.get('message')
        response = ask_ai(
            context=context,
            message=message,
        )

        chat = Chat(
            user=request.user,
            message=message,
            response=response,
        )
        chat.save()

        return JsonResponse({
            'message': message,
            'response': response,
        })
    return render(request, 'chatbot.html', {'chats': chats})
