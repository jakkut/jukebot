<script>
	import { Song } from "$lib";

	let { data } = $props();
	let playlist = data;

	console.log(playlist);
</script>

<div class="bg-accent-grey rounded-lg px-6 py-4 shadow-lg">
	<h3 class="text-2xl font-bold mb-4 text-left">{playlist.playlist_title}</h3>
	<div>
		{#each playlist.songs.slice(0, 5) as song}
			<Song data={song} />
		{/each}
		{#if playlist.songs.length > 5}
			<p class="text-center text-gray-300 mt-2">And more...</p>
		{/if}
	</div>
</div>
