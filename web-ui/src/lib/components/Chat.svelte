<script>
    import LinearProgress from '@smui/linear-progress'
    import { PUBLIC_API_BASE_URL } from '$env/static/public'
    import { marked } from 'marked'
    import Button, { Label } from '@smui/button'
    import { afterUpdate } from 'svelte';

    let files
    let chatId;
    let pdfInfo  // will be set after server digestion
    let uploading = false
    let waitingReply = false
    let messages = []
    let question
    let messagesElement

    afterUpdate(() => {
        if (messages.length > 0) {
            scrollToBottom(messagesElement)
        }
    })

    async function uploadPDF() {
        const file = files[0]
        console.info('Uploading file:', file)
        uploading = true

        const formData = new FormData()
        formData.append('file', file)

        const response = await fetch(`${PUBLIC_API_BASE_URL}/chat/`, {
            method: 'POST',
            body: formData
        })

        const data = await response.json()

        chatId = data.id
        pdfInfo = {
            filename: file.name,
            summary: data.pdf_info.summary
        }

        uploading = false
        console.info(`New chat with ID: ${chatId}`)
    }

    async function sendMessage() {
        if (!question) return
        console.info('Sending message:', question)
        messages = [...messages, { role: 'user', content: question }]

        const toSendQuestion = question

        question = null
        waitingReply = true

        const response = await fetch(`${PUBLIC_API_BASE_URL}/chat/${chatId}/ask?question=${encodeURIComponent(toSendQuestion)}`, {
            method: 'POST',
        })

        const data = await response.json()

        messages = [...messages, ...data.messages]
        waitingReply = false
    }

    export async function reset() {
        console.info('Resetting chat')
        const prevChatId = chatId

        messages = []
        pdfInfo = null
        chatId = null
        question = null
        files = null

        // Destroy previous chat server-side
        if (prevChatId) {
            await fetch(`${PUBLIC_API_BASE_URL}/chat/${prevChatId}/destroy`, {
                method: 'POST'
            })
        }
    }

    function scrollToBottom(node) {
        node.scroll({ top: node.scrollHeight, behavior: 'smooth' })
    }

    // $: if (messages.length > 0) {
    //     tick()
    // }
</script>

{#if pdfInfo}
<div class="chat">
    <div bind:this={messagesElement} class="messages">
        <div class="assistant message-card">
            <p>
                Your PDF file "{pdfInfo.filename}" has been processed successfully.
            A summary is generated for you as below:
            </p>
        </div>

        <div class="assistant message-card">{@html marked.parse(pdfInfo.summary)}</div>

        <div class="assistant message-card">You can now ask questions about "{pdfInfo.filename}".</div>

        {#each messages as { role, content }, i}
            <div class="{role} message-card">
                <p>{content}</p>
            </div>
        {/each}
    </div>

    {#if waitingReply}
        <div class="waiting-reply-indicator"><LinearProgress indeterminate /></div>
    {/if}

    <form class="user-inputs" on:submit|preventDefault={sendMessage}>
        <input type="text" bind:value={question} placeholder="Ask about PDF" />
        <Button touch variant="raised" disabled={waitingReply}><Label>Send</Label></Button>
    </form>
</div>
{:else}
<div class="pdf-uploader">
    <label for="pdf">Please upload a PDF file:</label>
    <input accept="application/pdf" bind:files name="pdf" type="file"
        disabled={uploading}
        on:change={uploadPDF}/>
    {#if uploading}
        <div class="uploading-indicator"><LinearProgress indeterminate /></div>
    {/if}
</div>
{/if}

<style>
    .chat {
        height: 100%;
        width: 80%;
        min-width: 600px;
        max-width: 1000px;
        display: flex;
        flex-direction: column;
        margin: 0 auto;
    }

    .chat .messages {
        flex: 1;  /* take up all letf space */
        display: flex;
        flex-direction: column;
        gap: 20px;
        overflow: scroll;
        padding: 20px;
        border: 1px solid #ccc;

    }

    .chat .user-inputs {
        height: 60px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .user-inputs input[type=text] {
        flex: 1;
        height: 35px;
        padding: 0 6px;
        border: 1px solid #ccc;
    }

    .pdf-uploader {
        margin: 20px;
    }

    .uploading-indicator {
        margin: 10px 0;
    }

    .message-card {
        width: 50%;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 0 6px rgba(0, 0, 0, 0.3);
    }

    :global(.message-card p:first-child) {
        margin-top: 0;
    }
    :global(.message-card p:last-child) {
        margin-bottom: 0;
    }

    .message-card.assistant {
        width: 80%;
        background: #f6f6f6;
        align-self: start;
    }
    .message-card.user {
        background: #1778ff;
        color: #FFF;
        align-self: end;
    }
</style>
