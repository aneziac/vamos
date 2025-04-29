<script lang="ts">
    import { Button } from "$lib/components/ui/button/index.js";
    import { Input } from "$lib/components/ui/input/index.js";

    // https://help.openai.com/en/articles/7031512-whisper-audio-api-faq
    const validExtensions = ['.m4a', '.mp3', '.webm', '.mp4', '.mpga', '.wav', '.mpeg'];
    const baseServerURL = 'http://127.0.0.1:5000'

    import { audioData } from './audioData.js';
    import TrackHeading from '$lib/TrackHeading.svelte';
    import ProgressBarTime from '$lib/ProgressBarTime.svelte';
    import Controls from '$lib/Controls.svelte';
    import VolumeSlider from '$lib/VolumeSlider.svelte';
    import { onMount } from 'svelte';

    let trackIndex = 0;
    let audioFile: HTMLAudioElement | null = null;
    let trackTitle = null;
    let totalTrackTime: number;
    let audioUrl = null; // stores link to local version of uploaded audio



    onMount(() => {
        // audioFile = new Audio(audioData[trackIndex].url);
        // audioFile.onloadedmetadata = () => {
        // totalTrackTime = audioFile!.duration;
        // updateTime();
        // };
        resetFileInput()
        document.getElementById('myForm').reset();
    });

    let totalTimeDisplay = "loading...";
    let currTimeDisplay = "0:00:00";
    let progress = 0;
    let prog = progress;
    let totalTime = 0;
    let trackTimer: NodeJS.Timeout;

    function updateTime() {
        if (audioFile) {
            progress = audioFile.currentTime * (100 / totalTrackTime);
            prog = audioFile.currentTime;
            totalTime = totalTrackTime;
            let currHrs = Math.floor((audioFile.currentTime / 60) / 60);
            let currMins: any = Math.floor(audioFile.currentTime / 60);
            let currSecs: any = Math.floor(audioFile.currentTime - currMins * 60);

            let durHrs = Math.floor( (totalTrackTime / 60) / 60 );
            let durMins: any = Math.floor( (totalTrackTime / 60) % 60 );
            let durSecs: any =  Math.floor(totalTrackTime - (durHrs * 60 * 60) - (durMins * 60));

            if (currSecs < 10) currSecs = `0${currSecs}`;
            if (durSecs < 10) durSecs = `0${durSecs}`;
            if (currMins < 10) currMins = `0${currMins}`;
            if (durMins < 10) durMins = `0${durMins}`;

            currTimeDisplay = `${currHrs}:${currMins}:${currSecs}`;
            totalTimeDisplay = `${durHrs}:${durMins}:${durSecs}`;

            if (audioFile.ended) {
                toggleTimeRunning();
            }
        }


    }

    const toggleTimeRunning = () => {
        if (audioFile) {
            totalTime = totalTrackTime;
            if (audioFile.ended && currTimeDisplay == totalTimeDisplay) {
                isPlaying = false;
                progress = 0;
                prog = 0;
                currTimeDisplay = "0:00:00";
                clearInterval(trackTimer);
                console.log(`Ended = ${audioFile.ended}`);
            } else {
                trackTimer = setInterval(updateTime, 100);
            }
        }
    }


    // Controls
    let isPlaying = false;
    // $: console.log(`isPlaying = ${isPlaying}`)

    const playPauseAudio = () => {
        if (audioFile) {
            if (audioFile.paused) {
                toggleTimeRunning()
                audioFile.play();
                isPlaying = true;
            } else {
                toggleTimeRunning()
                audioFile.pause();
                isPlaying = false;
            }
        }
    }

    const rewindAudio = () => {
        if (audioFile) {
            audioFile.currentTime -= 10;
        }
    };

    const forwardAudio = () => {
        if (audioFile) {
            audioFile.currentTime += 10;
        }
    };

    const onScrub = () => {
        if (audioFile) {
            audioFile.currentTime = prog;
            updateTime();
        }
    }

    // Volume Slider
    let vol = 50;

    const adjustVol = () => {
        if (audioFile) {
            audioFile.volume = vol / 100;
        }
    };

    let youtubeLink = '';
    let uploadedFile = '';

    let taskId: string | null = null;
    let statusMessage: string = '';
    let transcript: string = '';
    let output: string = '';
    let formattedTranscript: Array<[string, string]> = [];

    function selectRow(timestamp: string) {
        let time = Number(timestamp.slice(0, 2)) * 60 + Number(timestamp.slice(3, 5)) + Number(timestamp.slice(6, 7)) * 0.1;
        audioFile!.currentTime = time;
        updateTime();
    }

    function formatTranscript(transcript: string) : Array<[string, string]> {
        console.log(transcript);
        const splitText = transcript.split('\n');

        let result: Array<[string, string]> = [];

        for (let i = 0; i < splitText.length - 2; i += 3) {
            let startTime = splitText[i + 1].split(' ')[0];
            let importantPart = startTime.slice(3, 10).replace(',', '.');

            let text = splitText[i + 2];

            result.push([
                importantPart, text
            ])
        }

        console.log(result);

        return result;
    }

    async function pollTaskStatus(taskId: string) {
        const interval = setInterval(async () => {
            const response = await fetch(`${baseServerURL}/status/${taskId}`);
            const data = await response.json();

            if (data.status === 'complete' || data.status === 'failed') {
                clearInterval(interval);
                resetFileInput();
            }
            if (data.status === 'complete') {
                transcript = data.transcript;
                formattedTranscript = formatTranscript(transcript);
            }

            statusMessage = data.message;
        }, 1000); // Poll every 5 seconds
    }
    //async function checkFileExists(taskId: string) {
       //const response = await fetch(`${baseServerURL}/file-exists/${taskId}`);
        //if (response.ok) {
            //const data = await response.json();
            //return data.exists;
        //}
        //return false;
        //}

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

            const file = [...formData.entries()][0][1]; // little jank
            audioUrl = URL.createObjectURL(file);
            if (audioFile == null) {
                audioFile = new Audio(audioUrl);
                audioFile.onloadedmetadata = () => {
                    totalTrackTime = audioFile!.duration;
                    updateTime();
                };
            }

        } else {
            console.error("Failed to upload file: ", await response.text());
        }
    }

    // TODO: update to clear variables
    function resetFileInput() {
        uploadedFile = '';
        document.getElementById('file')!.value = '';
    }

    function downloadTranscript() {
    const blob = new Blob([formatSRT(transcript)], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'transcript.srt';
    document.body.appendChild(a); // Needed for Firefox
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    }

    function formatSRT(p: string) {
        let listsrt = p.split(/\r\n|\r|\n/);
        output = '';
        for (let i = 0; i < listsrt.length; i++) {
            if (i % 3 == 2) {
                output += listsrt[i].slice(1) + '\n' + '\n';
            }
            else {
                output += listsrt[i] + '\n';
            }
        }
        return output;
    }

    let fileInput;

    function openFileDialog() {
        fileInput.click();
    }

    function handleFileChange(event) {
        const file = event.target.files[0];
        if (file) {
            uploadedFile = file.name;
        } else {
            uploadedFile = '';
        }
    }
</script>

<!-- {#if transcript}
    <section class="download-action">
        <Button on:click={downloadTranscript} class="download-link">Download Transcript</Button>
    </section>
    {/if} -->
<div class="container mx-auto max-w-4xl justify-center items-center -mt-6">
    <div id ="button">  
        {#if transcript}
    <section class="download-action">
        <Button on:click={downloadTranscript} class="download-link">Download Transcript</Button>
    </section>
    {/if}
    {#if !transcript}
    <section id="yeet"></section>
    {/if}
    </div>
    <form on:submit={handleSubmit} enctype="multipart/form-data" id="myForm">
        <div id = "middle" class="flex rounded-2xl overflow-hidden bg-gray-100">
            <div class="group w-[70%]">
                <Input
                type="url"
                id="youtubeLink"
                name="youtubeLink"
                bind:value={youtubeLink}
                placeholder="Enter a Youtube URL..."
                disabled={uploadedFile != ''}
                class="outline-none py-10 pl-10 bg-transparent focus:outline-none border-0 focus:ring-0 focus:ring-transparent shadow-none rounded-none text-lg text-black"
                />
            </div>
            <div class="group relative w-[30%]">
                <input
                type="file"
                id="file"
                name="fileToUpload"
                accept={validExtensions.join(',')}
                on:change={handleFileChange}
                disabled={youtubeLink !== ''}
                bind:this={fileInput}
                class="hidden w-0"
                />

                <Button
                type="button"
                class="outline-none py-10 w-full bg-transparent rounded-none border-0 focus:ring-0 focus:ring-transparent shadow-none text-lg"
                on:click={openFileDialog}
                >
                {#if uploadedFile == ''}
                or upload a file...
                {:else}
                {uploadedFile}
                {/if}

            </Button>
            {#if uploadedFile != ''}
            <Button
            type="button"
            on:click={resetFileInput}
            class="absolute right-2 top-1/4 bg-red-300 text-white hover:bg-red-400 transition-colors duration-200 whitespace-nowrap rounded-full px-2 py-1 text-sm">X</Button>
            {/if}
        </div>

        <div class="flex justify-center">
            <Button
            type="submit"
            class="py-10 bg-gray-400 rounded-none hover:bg-green-700"
            >
            Submit
        </Button>
    </div>
</div>
</form>

{#if statusMessage}
<p>{statusMessage}</p>
{/if}

{#if transcript}

<div class="scroll-box">
    {#if audioUrl}
    <div id="player-cont">
        <TrackHeading {trackTitle} />
        <ProgressBarTime {currTimeDisplay}
        {totalTimeDisplay}
        {totalTime} bind:prog on:input={onScrub}/>
        <div id="controls">
            <Controls {isPlaying}
            on:rewind={rewindAudio}
            on:playPause={playPauseAudio}
            on:forward={forwardAudio} />
        </div>
        <div id="volume">
            <VolumeSlider bind:vol
            on:input={adjustVol} />
        </div>
    </div>

    <!-- <pre id="text1">{formattedTranscript}</pre> -->
    <div class="flex flex-col overflow-y-scroll overflow-x-hidden">
        {#each formattedTranscript as [timestamp, phrase]}
          <button
            type="button"
            class="grid [grid-template-columns:20%_80%] gap-4 p-2 hover:bg-gray-200 cursor-pointer rounded text-left"
            on:click={() => selectRow(timestamp)}
          >
            <div class="text-right pr-4 font-mono">[{timestamp}]</div>
            <div class="text-left">{phrase}</div>
          </button>
        {/each}
      </div>
    {/if}
    {#if !audioUrl}
    <div id = "text1" class="flex flex-col overflow-y-scroll overflow-x-hidden">
        {#each formattedTranscript as [timestamp, phrase]}
        <button
          type="button"
          class="grid [grid-template-columns:20%_80%] gap-8 p-2 hover:bg-gray-200 cursor-pointer rounded text-left"
          on:click={() => selectRow(timestamp)}
        >
          <div class="text-right pr-4 font-mono">[{timestamp}]</div>
          <div class="text-left">{phrase}</div>
        </button>
      {/each}
    </div>
    {/if}
</div>
{/if}
</div>

<style>
    pre {
        white-space: pre-wrap;
        word-wrap: break-word;
        overflow-x: hidden;
    }
    .scroll-box {
        position: relative;
        background-color: rgb(216, 228, 233);
        border: 3px solid white;
        overflow-y: auto;
        overflow-x: hidden;
        color: black;
        display: flex;
        flex-direction: column;
        margin-top: .1rem;
        width: 100%;
        max-height: calc(100vh - 340px);
    }
    #text1 {
        flex: 1 1 auto;
        padding: 1rem;
        font-family: 'Quicksand', sans-serif;
    }

    #player-cont {
        flex: 0 0 auto;
        background: rgba(28, 82, 103, 0.5);
        padding: 1rem;
        border-bottom: 1px solid #ccc;
     }

    #controls {
        /* display:inline-block; */
        float: left;
    }

    #volume {
        float: right;
        margin-left: 10px;
        margin: 5px;
    }

    .download-action {
        text-align: center;
        margin-right: 41rem;
        padding-right: 2rem;
        padding-left: 2rem;
        /* margin-bottom: -1rem; */
        margin-top: -3rem;
    }
    #yeet {
        margin-bottom: 3rem;
    }
    #middle {
        margin-top:1rem;
    }
</style>
