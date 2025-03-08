<script lang="ts">
// https://help.openai.com/en/articles/7031512-whisper-audio-api-faq
const validExtensions = ['.m4a', '.mp3', '.webm', '.mp4', '.mpga', '.wav', '.mpeg'];
let taskId: string | null = null;
let statusMessage: string = '';
let transcript: string = '';
// import { writeFileSync } from 'fs';

async function pollTaskStatus(taskId: string) {
    const interval = setInterval(async () => {
        const response = await fetch(`http://127.0.0.1:5000/status/${taskId}`);
        const data = await response.json();

        if (data.status === 'complete' || data.status === 'failed') {
            clearInterval(interval);
        }
        if (data.status === 'complete') {
            transcript = data.transcript;
        }

        statusMessage = data.message;
    }, 5000); // Poll every 5 seconds
}

async function handleSubmit(event: Event) {
    event.preventDefault();

    const formData = new FormData(event.target as HTMLFormElement);
    const response = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
    });

    if (response.ok) {
        const data = await response.json();
        taskId = data.task_id as string;
        statusMessage = data.message;
        pollTaskStatus(taskId);

        // const { fileToUpload } = formData as { fileToUpload: File };
        // writeFileSync(`static/${fileToUpload.name}`, Buffer.from(await fileToUpload.arrayBuffer()));

    } else {
        console.error("Failed to upload file: ", await response.text());
    }
}
</script>

<div class="container h-full mx-auto flex justify-center items-center">
    <form on:submit={handleSubmit} enctype="multipart/form-data">
        <div class="group">
            <label for="file">Upload your file</label>
            <input
                type="file"
                id="file"
                name="fileToUpload"
                accept={validExtensions.join(',')}
                required
            />
        </div>

        <button type="submit">Submit</button>
    </form>
    {#if statusMessage}
        <p>{statusMessage}</p>
    {/if}

    {#if transcript}
        <div class="scroll-box">

            <p>{transcript}</p>

        </div>

    {/if}
</div>
<style>

    .scroll-box {
    height: 50%;
    overflow-y: auto;
    padding: 50px ;
    margin: 30px auto;
    border: 5px solid white;
    color: black;
    background-color: lightcyan;
    text-align: center;
    position: fixed;
    top: 120px ;
    left: auto;
    right: auto;
    width: 50%;
    }

    </style>