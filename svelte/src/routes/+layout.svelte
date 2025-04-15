<script lang="ts">
	import "../app.css";

	let { children } = $props();
</script>

<svelte:head>
	<title>Jukebot</title>
</svelte:head>

<div>
	{@render children()}
</div>
