<script lang="ts">
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
    let trackTitle = audioData[trackIndex].name;
    let totalTrackTime: number;

    onMount(() => {
        audioFile = new Audio(audioData[trackIndex].url);
        audioFile.onloadedmetadata = () => {
        totalTrackTime = audioFile!.duration;
        updateTime();
        };
    });

    let totalTimeDisplay = "loading...";
	let currTimeDisplay = "0:00:00";
	let progress = 0;
	let trackTimer: NodeJS.Timeout;

	function updateTime() {
		if (audioFile) {
			progress = audioFile.currentTime * (100 / totalTrackTime);
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
			if (audioFile.ended) {
				isPlaying = false;
				clearInterval(trackTimer);
				console.log(`Ended = ${audioFile.ended}`);
			} else {
				trackTimer = setInterval(updateTime, 100);
			}
		}
	}


	// Controls
	let isPlaying = false;
	$: console.log(`isPlaying = ${isPlaying}`)

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

	// const forwardAudio = () => audioFile.currentTime += 10;

	// Volume Slider
	let vol = 50;

	const adjustVol = () => {
		if (audioFile) {
			audioFile.volume = vol / 100;
		}
	};
    
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
                    class = "mb-4"
                />
            </div>
    
            <!-- <button type="submit">Submit</button> -->
            <div class="flex justify-center">
                <button 
                    type="submit"
                    style="background-color: #6cb4ac;"
                    class="text-white font-bold py-2 px-6 rounded-full shadow-lg transition-all duration-300 ease-in-out hover:scale-105 mb-3"
                >
                    Submit
                </button>
            </div> 

            <section id="player-cont">
                <TrackHeading {trackTitle} />
                <ProgressBarTime {currTimeDisplay}
                                 {totalTimeDisplay}
                                 {progress} />
                <Controls {isPlaying}
                    on:rewind={rewindAudio}
                    on:playPause={playPauseAudio}
                    on:forward={forwardAudio} />
                <VolumeSlider bind:vol
                              on:input={adjustVol} />
            </section>
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

        #player-cont {
            width: 300px;
            height: 165px;
            padding: .7rem 1.5rem 0;
            box-shadow: 0 0 5px black;
            background: #222;
            color: #bbb;
            border-radius: 5px 5px 0 0;
        }
    
        .group{
            
        }
    </style>
    