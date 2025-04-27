<script lang="ts">
    import '../app.postcss'

	let { children } = $props();
</script>

<!-- <h1 class="maintitle">VAMOS</h1> -->
<!-- <nav>
    <a href="/">Home</a>
    <a href="/about">About</a>
    <a href="/settings">Settings</a>
</nav> -->

{@render children()}

<style>
	.maintitle {
		color: black;
		font-size: 90px;
		text-align: center;
		margin-top: 30px;
		font-style: normal;
		font-family: 'Cal Sans', sans-serif;
		margin: 50px auto;
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
