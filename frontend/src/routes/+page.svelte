<script lang="ts">
// https://help.openai.com/en/articles/7031512-whisper-audio-api-faq
const validExtensions = ['.m4a', '.mp3', '.webm', '.mp4', '.mpga', '.wav', '.mpeg'];
let taskId: string | null = null;
let statusMessage: string = '';

async function pollTaskStatus(taskId: string) {
    const interval = setInterval(async () => {
        const response = await fetch(`http://127.0.0.1:5000/status/${taskId}`);
        const data = await response.json();

        if (data.status === 'complete' || data.status === 'failed') {
            clearInterval(interval);
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
</div>
