<script lang="ts">
	import { audioData } from './audioData.js';

	import TrackHeading from '$lib/TrackHeading.svelte';
	import ProgressBarTime from '$lib/ProgressBarTime.svelte';
	import Controls from '$lib/Controls.svelte';
	import VolumeSlider from '$lib/VolumeSlider.svelte';
	// import PlayList from './PlayList.svelte';

	// Get Audio track
	let trackIndex = 0;
	// $: console.log(trackIndex)
	let audioFile = new Audio(audioData[trackIndex].url);
	let trackTitle = audioData[trackIndex].name;

	const loadTrack = () => {
		audioFile = new Audio(audioData[trackIndex].url);
		audioFile.onloadedmetadata = () => {
			totalTrackTime = audioFile.duration;
			updateTime();
		}
		trackTitle = audioData[trackIndex].name;
	}

	// const autoPlayNextTrack = () => {
	// 	if (trackIndex <= audioData.length-1) {
	// 		trackIndex += 1;
	// 		loadTrack();
	// 		audioFile.play();
	// 	} else {
	// 		trackIndex = 0;
	// 		loadTrack();
	// 		audioFile.play();
	// 	}
	// }


	// Track Duration and Progress Bar
	let totalTrackTime: number;
	$: console.log(totalTrackTime)
	audioFile.onloadedmetadata = () => {
		totalTrackTime = audioFile.duration;
		updateTime();
	}

	let totalTimeDisplay = "loading...";
	let currTimeDisplay = "0:00:00";
	let progress = 0;
	let trackTimer: NodeJS.Timeout;

	function updateTime() {
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

	const toggleTimeRunning = () => {
		if (audioFile.ended) {
			isPlaying = false;
			clearInterval(trackTimer);
			console.log(`Ended = ${audioFile.ended}`);
		} else {
			trackTimer = setInterval(updateTime, 100);
		}
	}


	// Controls
	let isPlaying = false;
	$: console.log(`isPlaying = ${isPlaying}`)

	const playPauseAudio = () => {
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

	const rewindAudio = () => audioFile.currentTime -= 10;
	const forwardAudio = () => audioFile.currentTime += 10;

	// Volume Slider
	let vol = 50;
	const adjustVol = () => audioFile.volume = vol / 100;


	// Playlist
	// const handleTrack = (e) => {
	// 	if (!isPlaying) {
	// 		trackIndex = Number(e.target.dataset.trackId);
	// 		loadTrack();
	// 		playPauseAudio(); // auto play
	// 	} else {
	// 		isPlaying = false;
	// 		audioFile.pause();
	// 		trackIndex = Number(e.target.dataset.trackId);
	// 		loadTrack();
	// 		playPauseAudio(); // auto play
	// 	}
	// }
</script>


<main>
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

		<!-- <PlayList on:click={handleTrack} /> -->
</main>

<style>
/* main {
    width: 100vw;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 0 0 0;
    background-color: #ddd;
} */

#player-cont {
    width: 250px;
    height: 165px;
    padding: .7rem 1.5rem 0;
    box-shadow: 0 0 5px black;
    background: #222;
    color: #bbb;
    border-radius: 5px 5px 0 0;
}
</style>
