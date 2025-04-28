<script lang="ts">
    import '../app.postcss'

	let { children } = $props();
</script>

	<h1 class="maintitle">VAMOS</h1>
	<nav>
		<a href="/">Home</a>
		<a href="/about">About</a>
		<!-- <a href="/settings">Settings</a> -->
	</nav>


<!-- <div class="h-[100%] bg-[url('/mountains.jpg')] bg-cover bg-left p-4">
</div> -->


{@render children()}

<style>
	:global(body) {
		@apply bg-[url('/mountains.jpg')];
		background-repeat: no-repeat;
		background-attachment: fixed;
		background-position: center; 
		background-size: cover;
		font-family: 'Quicksand', sans-serif; 
	}
	.maintitle {
		color: black;
		font-size: 90px;
		text-align: center;
		margin-top: 60px;
		font-style: normal;
		font-family: 'Cal Sans', sans-serif;
		/* margin: 20px auto; */
	}

	nav {
		font-size: 20px;
		display:flex;
		justify-content: center;
		width: 20vw;
		gap: 2rem;
		margin: 25px auto;
		box-sizing: border-box;
	}

	nav a {
		text-align: center;
		color: black;
		background-color: rgba(240, 248, 255, 0.5);
		border-radius: 1.5rem;
		padding: 2px 13px;
	}


</style>
