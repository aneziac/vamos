<script lang="ts">
    import '../app.postcss'

	let { children } = $props();
</script>

<style>
	.maintitle {
		color: black;
		font-size: 75px;
		text-align: center;
		margin-top: 50px;
		font-style: normal;
	}

	nav {
		font-size: 20px;
		display:flex;
		justify-content: space-between;
		width: 20vw;
		margin: 50px auto;
	}

	nav a {
		text-align: center;
		color: black;
		background-color: rgba(240, 248, 255, 0.5);
		border-radius: 1.5rem;
		width: 110%;
		padding: 2px 15px;
	}
</style>


	<h1 class="maintitle">VAMOS</h1>
	<nav>
		<a href="/">Home</a>
		<a href="/about">About</a>
		<a href="/settings">Settings</a>
	</nav>



{@render children()}
