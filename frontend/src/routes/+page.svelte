<script lang="ts">
    // https://help.openai.com/en/articles/7031512-whisper-audio-api-faq
    const validExtensions = ['.m4a', '.mp3', '.webm', '.mp4', '.mpga', '.wav', '.mpeg']
</script>

<div class="container h-full mx-auto flex justify-center items-center">
    <form method="post" enctype="multipart/form-data">
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
</div>
