# relatorioCustomizadoRefeitorios

 - 1º É necessario que o usuario possua login na plataforma IDSECURE
 - 2º Na plataforma do IDSECURE é de extrema importancia, ter bem definido os Grupos.
 - 3º O usuario defini a data inicial e final para que os relatórios sejam criados e após clicar em GERAR RELATÓRIO, tudo é executado autoMÁGICAMENTE.. 


## 🎥 Demonstração do Sistema
<p align="center">
  <img src="assets\DEMO.gif" width="800">
</p>



# Motivação:

Este sistema foi desenvolvido para resolver desafios reais de gestão de restaurantes e refeitórios com o objetivo gerar insights, provenientes de um sistemas de controle de entrada e saída de pessoas de catraca, a aplicação centraliza dados operacionais e os transforma em informações úteis para análise e tomada de decisão.

A solução permite identificar rapidamente eventos relevantes, de relatórios consolidados como :

 - Tipo de reifeição e quantidade consumida por empresa.
 - Evidências de dia da semana, com maior volume de refeições
 - Horários de Pico no refeitório, distribuído por Hora.
 - Quantidade de Refeições por Empresa.
 - Indicadores de Desempenho
 - Monitoramento de consumo de refeições Mês a Mês
 - Resumo de refeições por Empresa
 - Extrato Financeiro



# Tecnologias Utilizadas

A aplicação foi construída utilizando Python e uma interface interativa baseada em Streamlit, permitindo que os usuários consultem informações de forma simples, rápida e visual.
O sistema realiza a autenticação no endpoint da API, consome os dados disponibilizados, aplica regras de tratamento de dados, organiza e entrega um relatório padronizado, confiável e pronto para análise.

## Este projeto foi desenvolvido utilizando as seguintes tecnologias:

 - Python

 - Streamlit – criação da interface web interativa

 - Pandas – processamento e análise de dados

 - Requests – integração com APIs externas

´´´
restaurantesapi/
│
├── main.py                 
├── utilitarios.py          
├── requirements.txt        
├── README.md               
│
├── pages/
│   ├── login.py            
│   ├── home.py             
│   ├── dashboard.py        
│   └── relatorios.py       
│
└── assets/
    ├── logo_branco.png     
    ├── logo_preto.png      
    └── demo.gif  
´´´