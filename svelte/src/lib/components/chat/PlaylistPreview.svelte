<script>
	import { Song } from "$lib";

	let { id } = $props();

	// Do something to fetch the actual playlist info
	let dummyPlaylist = {
		title: "Playlist Name",
		description: "Playlist Description",
		songs: [
			{ title: "Hillbilly Elegy", artist: "Taylor Swift" },
			{ title: "Knock", artist: "Bruv" },
		],
	};

	let playlist = dummyPlaylist;
</script>

<div class="bg-accent-grey rounded-lg px-6 py-4">
	<h3 class="text-xl font-bold">{playlist.title}</h3>
	<h4 class="">{playlist.description}</h4>
	<div>
		{#each playlist.songs as song}
			<Song data={song} />
		{/each}
	</div>
</div>
