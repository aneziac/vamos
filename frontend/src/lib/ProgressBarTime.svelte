<script>
	export let currTimeDisplay;
	export let totalTimeDisplay;
	export let totalTime;
	/**
	 * @type {any}
	 */
	 export let prog;
	// export let progress;

</script>


<div id="time">
	<span id="progress-time">{currTimeDisplay}</span>
	<span id="track-duration">{totalTimeDisplay}</span>
</div>

<div id="progress-bar-cont">
	<!-- <span id="bar" style="width: {progress}%"></span> -->
	<!-- <input class='trackslider'
    style="width: {progress}%"
	on:click={() => dispatch('scrub')}
	type = 'range'
	max={totalTimeDisplay}
    min={0}
    value={progress}/> -->

	<input id="slider" 
	class="trackslider"
	type="range" 
	min="0" 
	max="{totalTime}"
	style="width: 100%"
	bind:value={prog}
	on:input

	/>
</div>


<style>
	#slider {
		color:aqua;
	}
	#time {
		width: 100%;
		display: flex;
		justify-content: space-between;
	}

	/* #progress-bar-cont {
		width: 100%;
		height: 10px;
		margin: .5rem 0 .5rem;
		display: flex;
		align-items: center;
		border: 1px solid #888;
		cursor: pointer;
	} */

	/* #bar {
		width: 0%;
		height: 10px;
		background-color: goldenrod;
	} */
</style>