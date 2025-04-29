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
            }

            statusMessage = data.message;
        }, 5000); // Poll every 5 seconds
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

            console.log(formData)
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
        console.clear();
    }

    function downloadTranscript() {
    const blob = new Blob([transcript], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'transcript.txt';
    document.body.appendChild(a); // Needed for Firefox
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
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

<!-- <div class="flex flex-col h-screen overflow-hidden"> -->
    <!-- <div class="h-[1%] bg-gradient-to-t from-gray-500 to-gray-900 p-4">
    </div> -->
    <!-- <div class="h-[100%] bg-[url('/mountains.jpg')] bg-cover bg-left p-4"> -->
        <!-- <h1 class="maintitle mt-10">VAMOS</h1> -->
        <div class="container mx-auto max-w-4xl justify-center items-center">
            <form on:submit={handleSubmit} enctype="multipart/form-data" id="myForm">
                <div class="flex rounded-2xl overflow-hidden bg-gray-100">
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

            <!-- {#if audioUrl}
            <audio controls src={audioUrl}></audio>
            <section id="player-cont">
                <TrackHeading {trackTitle} />
                <ProgressBarTime {currTimeDisplay}
                {totalTimeDisplay}
                {totalTime} bind:prog on:input={onScrub}/>
                <Controls {isPlaying}
                on:rewind={rewindAudio}
                on:playPause={playPauseAudio}
                on:forward={forwardAudio}/>
                <VolumeSlider bind:vol
                on:input={adjustVol} />
            </section>
            {/if} -->


            {#if statusMessage}
                <p>{statusMessage}</p>
            {/if}

            {#if transcript}
            <!-- <section class="download-action">
                <a href={`/download/${taskId}`} download class="download-link">Download Transcript</a>
            </section> -->
            <section class="download-action">
                <Button on:click={downloadTranscript} class="download-link">Download Transcript</Button>
            </section>
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
                <pre id="text1">{transcript}</pre>
                {/if}
                {#if !audioUrl}
                <pre id="text2">{transcript}</pre>
                {/if}
            </div>



            {/if}
        </div>
    <!-- </div> -->
    <!-- <div class="h-[1%] bg-gradient-to-b from-gray-700 to-gray-900 p-4">
    </div> -->
<!-- </div> -->


<style>
    pre {
        white-space: pre-wrap;
        word-wrap: break-word;
        overflow-x: hidden;
    }
    .scroll-box {
        height: 47vh;
        overflow-y: scroll;
        /* padding: 50px; */
        margin: 30px auto;
        border: 3px solid white;
        color: black;
        background-color: rgb(216, 228, 233);
        text-align: center;
        position: fixed;
        left: 15vw;
        right: 15vw;
        top: 45vh ;
        width: 70vw;
    }
    #text1 {
        z-index: 10;
        height: 60%;
        overflow-y: scroll;
        font-family: 'Quicksand', sans-serif; 
    }

    #text2 {
        z-index: 10;
        height: 100%;
        overflow-y: scroll;
        padding: 20px;
        font-family: 'Quicksand', sans-serif; 
    }
    #player-cont {
        background: rgba(28, 82, 103, 0.5);
        width: 100%;
        padding: .5rem 1.5rem;
        padding-bottom: 3rem;
        margin-bottom: 1rem;
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
        margin-top: 20px;
        position: fixed;
        top: 25vh;
    }


    .download-link {
        padding: 10px 20px;
        background-color: #4CAF50;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        font-size: 16px;
    }


    .download-link:hover {
        background-color: #45a049;
    }
</style>
