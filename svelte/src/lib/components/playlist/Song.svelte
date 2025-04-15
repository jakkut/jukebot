<script>
	let { data } = $props();
</script>

<div class="flex bg-back-grey my-2 p-2">
	<img alt="album cover" />
	<p class="mr-auto">{data.title}</p>
	<p>{data.artist}</p>
</div>
