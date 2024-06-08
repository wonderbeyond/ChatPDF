<script>
    import Chat from '$lib/components/Chat.svelte'
    let chatComponent
</script>

<div id="app">
    <header>
        <span class="brand">ChatPDF Demo by Wonder</span>
        <button class="new-chat-btn" on:click="{chatComponent.reset}">New Chat</button>
    </header>
    <div id="main">
        <Chat bind:this={chatComponent} />
    </div>
</div>

<style>
    :global(html, body) {
        margin: 0;
        padding: 0;
        height: 100%;
    }

    #app {
        display: flex;
        height: 100vh;
        flex-direction: column;
        align-items: center;
    }

    header {
        width: 100%;
        height: 40px;
        box-shadow: 0 0 6px #EEE;
        background-color: #F0F0F0;
        display: flex;
        margin: 0 auto;
        align-items: center;
        justify-content: space-between;
        gap: 60px;
    }

    header .brand {
        font-weight: bold;
        margin-left: 20px;
    }
    header .new-chat-btn {
        cursor: pointer;
        margin-right: 20px;
    }

    #main {
        min-height: 0;
        flex: 1;
        /* border: 3px solid red; */
    }
</style>
