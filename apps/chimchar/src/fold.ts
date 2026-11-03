// Code
/**
 * Lower case without accents, so "indice" finds "Índice".
 * Keeps the length: position i of the result is position i of text.
 */
export function fold(text: string): string {

    let folded = ''

    for (const char of text.split('')) {
        const plain = char.normalize('NFD')
            .replace(/\p{Diacritic}/gu, '')
            .toLowerCase()
        folded += plain.length === 1 ? plain : char
    }

    return folded
}
