import os
from dotenv import load_dotenv
from typing import final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler,filters,ContextTypes, ConversationHandler
import gemini
import link_shorterner as shorting
from keep_alive import keep_alive

load_dotenv('.env')
TOKEN: final = os.getenv('Telegram_Token')
BOT_USERNAME: final = os.getenv('Bot_Username')

#define status for conversation
asking_link = 1

#bot comment when user first time use it
async def start_command (update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await update.message.reply_text('Ini chat bot Gemini silahkan chat seperti biasa.')

#conversation for link shorterner
async def conversation_1  (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('silahkan berikan link yang akan disingkat disingkat atau ketik /exit untuk keluar')
    return asking_link #fungsinya supaya bot tetap di percakapan
async def shorter_link_command (update: Update, context: ContextTypes.DEFAULT_TYPE): 
    text:str = update.message.text
    print(f'User ({update.message.chat.id}): "{text}"')
    if text.lower() == '/exit':
        await update.message.reply_text('percakapan ini diakhiri.')
        return ConversationHandler.END
    shortered_link = shorting.shorter_link(text)
    response = f'ini link yang telah disingkat:\n{shortered_link}\n /exit jika ingin keluar atau masukkan link lainnya.  '
    await update.message.reply_text(response)
    save_conversation(update.message.chat.first_name,text,response,update.message.chat.id)
    return asking_link

#how the bot response to user input
async def handle_message (update:Update, context:ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text:str = update.message.text
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
    if message_type == 'group' and BOT_USERNAME in text:
        new_text:str = text.replace(BOT_USERNAME,'').strip()
        response:str = gemini.gemini(new_text)
    else:
        response:str = gemini.gemini(text)
    await update.message.reply_text(response)
    save_conversation(update.message.chat.first_name,text,response,update.message.chat.id)

def save_conversation(username, user_message, Bot_respond,user_id):
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, 'user_data', str(username)+ '.txt')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path,"a") as file:
        file.write(f'User({user_id}): {user_message}\nBot Respond: {Bot_respond}\n -----------------\n')
        
async def cancel(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('percakapan ini diakhiri.')
    return ConversationHandler.END

async def error(update:Update, context:ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} causes error {context.error}')
    await update.message.reply_text('maaf input invalid. Silahkan masukkan input yang lain')


if __name__ == '__main__':
    keep_alive()
    print('starting the bot...')
    app = Application.builder().token(TOKEN).build()
    
    link_shorterner = ConversationHandler(
        entry_points=[CommandHandler('shorter_link',conversation_1)],
        states={
            asking_link: [MessageHandler(filters.TEXT &(~filters.COMMAND), shorter_link_command)],},
        fallbacks=[CommandHandler('exit',cancel)]
    )
    app.add_handler(link_shorterner)
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_error_handler(error)
    
    #poll the bot
    print('polling...')
    app.run_polling(poll_interval=1)
