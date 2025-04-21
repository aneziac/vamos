<script lang="ts">
// https://help.openai.com/en/articles/7031512-whisper-audio-api-faq
const validExtensions = ['.m4a', '.mp3', '.webm', '.mp4', '.mpga', '.wav', '.mpeg'];
const baseServerURL = 'http://127.0.0.1:5000'

let youtubeLink = '';
let uploadedFile = false;

let taskId: string | null = null;
let statusMessage: string = '';
let transcript: string = '';
// import { writeFileSync } from 'fs';

async function pollTaskStatus(taskId: string) {
    const interval = setInterval(async () => {
        const response = await fetch(`${baseServerURL}/status/${taskId}`);
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

    let endpoint = "";
    if (formData.has("fileToUpload")) {
        endpoint = "upload";
    } else if (formData.has("youtubeLink")) {
        endpoint = "video";
    }

    const response = await fetch(`${baseServerURL}/${endpoint}`, {
        method: "POST",
        body: formData,
    });

    if (response.ok) {
        const data = await response.json();
        taskId = data.task_id as string;
        statusMessage = data.message;
        pollTaskStatus(taskId);

        // @ts-ignore
        // const { fileToUpload } = formData as { fileToUpload: File };
        // writeFileSync(`static/${fileToUpload.name}`, Buffer.from(await fileToUpload.arrayBuffer()));

    } else {
        console.error("Failed to upload file: ", await response.text());
    }
}

function resetFileInput() {
    uploadedFile = false;
    document.getElementById('file')!.value = '';
}
</script>


<div class="container h-full mx-auto flex flex-col justify-center items-center">
    <form on:submit={handleSubmit} enctype="multipart/form-data">
        <div class="group">
            <label for="file">Upload your file</label>
            <input
                type="file"
                id="file"
                name="fileToUpload"
                accept={validExtensions.join(',')}
                on:change={_ => uploadedFile = true}
                disabled={youtubeLink !== ''}
            />
            {#if uploadedFile}
                <button type="button" on:click={resetFileInput}>Delete File</button>
            {/if}
        </div>

        <div class="group">
            <label for="youtubeLink">Or provide a YouTube link</label>
            <input
                type="url"
                id="youtubeLink"
                name="youtubeLink"
                bind:value={youtubeLink}
                placeholder="Enter YouTube URL"
                disabled={uploadedFile}
            />
        </div>

        <button type="submit">Submit</button>
    </form>

    {#if statusMessage}
        <p>{statusMessage}</p>
    {/if}

    {#if transcript}
        <div class="scroll-box">

            <pre>{transcript}</pre>

        </div>

    {/if}
</div>

<style>
    .scroll-box {
        height: 700px;
        overflow-y: auto;
        padding: 50px;
        margin: 30px auto;
        border: 5px solid white;
        color: black;
        background-color: lightcyan;
        text-align: center;
        position: float;
        top: 120px ;
        left: auto;
        right: auto;
        width: 75%;
        white-space: normal;
    }

    .group{
        
    }
</style>
