/*
 * Copyright 2012-2025 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.springframework.samples.petclinic.owner;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.FilterType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.validation.BeanPropertyBindingResult;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.BDDMockito.given;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.model;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(value = PetController.class,
        includeFilters = @ComponentScan.Filter(value = PetTypeFormatter.class, type = FilterType.ASSIGNABLE_TYPE))
class VesperPetTypeReproductionTests {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private OwnerRepository owners;

    @MockitoBean
    private PetTypeRepository types;

    @Test
    void existingPetMustRejectMissingType() {
        Pet pet = new Pet();
        pet.setId(1);
        pet.setName("Milo");
        pet.setBirthDate(LocalDate.of(2020, 1, 1));
        BeanPropertyBindingResult errors = new BeanPropertyBindingResult(pet, "pet");
        new PetValidator().validate(pet, errors);
        assertTrue(errors.hasFieldErrors("type"), "pets.type_id is NOT NULL: editing must reject a missing type");
    }

    @Test
    void editMustRejectClearedType() throws Exception {
        PetType type = new PetType();
        type.setId(1);
        type.setName("cat");
        Pet pet = new Pet();
        pet.setId(1);
        pet.setName("Milo");
        pet.setType(type);
        pet.setBirthDate(LocalDate.of(2020, 1, 1));
        Owner owner = new Owner();
        owner.setId(1);
        owner.addPet(pet);
        given(this.owners.findById(1)).willReturn(Optional.of(owner));
        given(this.types.findPetTypes()).willReturn(List.of(type));
        this.mockMvc.perform(post("/owners/1/pets/1/edit").param("name", "Milo")
                .param("birthDate", "2020-01-01").param("type", ""))
            .andExpect(status().isOk())
            .andExpect(model().attributeHasFieldErrors("pet", "type"));
    }

}
